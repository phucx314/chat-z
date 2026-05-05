"""
Main window — refactored to use FastAPI server via httpx.
All conversation state comes from the server.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QPushButton, QInputDialog, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPixmap
import httpx

from core.llm_client import LLMWorker, SERVER_URL
from ui.sidebar import Sidebar
from ui.chat_area import ChatArea
from ui.input_area import ChatInputArea
from ui.settings_dialog import SettingsDialog
from ui.styles import BG_CHAT, BG_HEADER, TEXT_PRIMARY, TEXT_MUTED, ACCENT, BORDER, SUCCESS

import core.history as history


class ConfigLoader(QThread):
    done = pyqtSignal(dict)
    def run(self):
        try:
            with httpx.Client(timeout=5) as c:
                res = c.get(f"{SERVER_URL}/config")
            self.done.emit(res.json() if res.status_code == 200 else {})
        except Exception:
            self.done.emit({})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # local config for UI defaults
        from core.config import load_config
        self.config_data  = load_config()
        self.current_conv_id: str | None = None

        self.setWindowTitle("AI Chat")
        self.resize(1100, 740)
        self.setMinimumSize(800, 540)

        central = QWidget()
        central.setStyleSheet(f"background-color: {BG_CHAT};")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.conv_selected.connect(self._load_conversation)
        self.sidebar.new_chat.connect(self._new_chat)
        self.sidebar.open_settings.connect(self._open_settings)
        root.addWidget(self.sidebar)

        # Right panel
        right = QWidget()
        right.setStyleSheet(f"background-color: {BG_CHAT};")
        right_ly = QVBoxLayout(right)
        right_ly.setContentsMargins(0, 0, 0, 0)
        right_ly.setSpacing(0)

        self.header = self._build_header()
        right_ly.addWidget(self.header)

        self.chat_area = ChatArea()
        right_ly.addWidget(self.chat_area, 1)

        self.input_area = ChatInputArea(self.config_data)
        self.input_area.send_requested.connect(self._on_send)
        right_ly.addWidget(self.input_area)

        root.addWidget(right, 1)
        self._startup_load()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self) -> QFrame:
        hdr = QFrame()
        hdr.setObjectName("chat_header")
        hdr.setFixedHeight(60)
        hdr.setStyleSheet(f"QFrame#chat_header {{ background-color: {BG_HEADER}; border-bottom: 1px solid {BORDER}; }}")

        ly = QHBoxLayout(hdr)
        ly.setContentsMargins(20, 0, 20, 0)
        ly.setSpacing(14)

        av = QLabel()
        av.setPixmap(self._make_avatar())
        av.setFixedSize(42, 42)
        ly.addWidget(av)

        info = QVBoxLayout()
        info.setSpacing(1)
        self.header_title  = QLabel("AI Assistant")
        self.header_title.setObjectName("chat_title")
        self.header_online = QLabel("● Active Now")
        self.header_online.setObjectName("chat_online")
        info.addWidget(self.header_title)
        info.addWidget(self.header_online)
        ly.addLayout(info)
        ly.addStretch()

        self.header_model = QLabel()
        self.header_model.setObjectName("header_model_lbl")
        self._refresh_header_model()
        ly.addWidget(self.header_model)
        return hdr

    def _make_avatar(self, size: int = 42) -> QPixmap:
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#1e2533")))
        p.setPen(QPen(QColor(ACCENT), 1.5))
        p.drawEllipse(2, 2, size-4, size-4)
        p.setPen(QPen(QColor(ACCENT)))
        font = p.font(); font.setPointSize(14); font.setBold(True)
        p.setFont(font)
        p.drawText(2, 2, size-4, size-4, Qt.AlignmentFlag.AlignCenter, "✦")
        p.end()
        return px

    def _refresh_header_model(self):
        p = self.config_data.get("provider", "OpenAI").split(" (")[0]
        m = self.config_data.get("model", "")
        self.header_model.setText(f"  {p}  ·  {m}  ")

    # ── Startup ───────────────────────────────────────────────────────────────
    def _startup_load(self):
        all_convs = history.get_all_conversations()
        for c in all_convs:
            if not c.get("messages") and c.get("title") == "New Chat":
                history.delete_conversation(c["id"])

        convs = history.get_all_conversations()
        if convs:
            self._load_conversation(convs[0]["id"])
        else:
            self._new_chat()

    # ── Conversation management ───────────────────────────────────────────────
    def _new_chat(self):
        conv = history.create_conversation()
        self.current_conv_id = conv["id"]
        self.displayed_messages = []
        self.chat_area.clear_chat()
        self.header_title.setText("AI Assistant")
        self.sidebar.refresh(select_id=conv["id"])
        self.input_area.focus_input()

    def _load_conversation(self, conv_id: str):
        conv = history.get_conversation(conv_id)
        if not conv:
            return
        self.current_conv_id = conv_id
        self.displayed_messages = conv.get("messages", []).copy()
        self.chat_area.load_messages(conv.get("messages", []))
        self.header_title.setText(conv.get("title", "AI Assistant"))
        self.sidebar.set_active(conv_id)

    # ── Settings ──────────────────────────────────────────────────────────────
    def _open_settings(self):
        dlg = SettingsDialog(self.config_data, self)
        if dlg.exec():
            saved = dlg.get_config()
            from core.config import load_config, save_config
            fresh = load_config()
            fresh["api_key"]  = saved.get("api_key", "")
            fresh["provider"] = saved.get("provider", fresh["provider"])
            fresh["base_url"] = saved.get("base_url", fresh["base_url"])
            fresh["allow_interrupt"] = saved.get("allow_interrupt", fresh.get("allow_interrupt", False))
            save_config(fresh)
            self.config_data = fresh

            # Push to server
            try:
                with httpx.Client(timeout=5) as c:
                    c.patch(f"{SERVER_URL}/config", json={
                        "provider": fresh["provider"],
                        "base_url": fresh["base_url"],
                        "api_key":  fresh.get("api_key", ""),
                        "model":    fresh.get("model", ""),
                        "allow_interrupt": fresh.get("allow_interrupt", False),
                    })
            except Exception:
                pass  # server may not be running

            self.input_area.update_config(self.config_data)
            self._refresh_header_model()

    # ── Send ──────────────────────────────────────────────────────────────────
    def _on_send(self, text: str):
        if not self.current_conv_id:
            return

        is_typing = hasattr(self, "pending_replies") and len(self.pending_replies) > 0
        if is_typing and not self.config_data.get("allow_interrupt", False):
            return

        # First message? update header title
        conv = history.get_conversation(self.current_conv_id)
        if conv and not conv.get("messages"):
            title = text[:40] + ("…" if len(text) > 40 else "")
            self.header_title.setText(title)
            history.rename_conversation(self.current_conv_id, title)
            self.sidebar.update_conv_title(self.current_conv_id, title)

        self.displayed_messages.append({"role": "user", "content": text})
        
        override_messages = None
        if is_typing:
            self.pending_replies = []
            override_messages = self.displayed_messages.copy()

        if not hasattr(self, "typing_run_id"):
            self.typing_run_id = 0
        self.typing_run_id += 1
        current_run_id = self.typing_run_id

        if not self.config_data.get("allow_interrupt", False):
            self.input_area.set_enabled(False)
            
        self.chat_area.add_message("user", text)
        self.chat_area.show_typing()

        model = self.config_data.get("model")
        self.worker = LLMWorker(self.current_conv_id, text, model, override_messages)
        self.worker.finished.connect(
            lambda replies, err, cid=self.current_conv_id, rid=current_run_id: self._on_reply(replies, err, cid, rid)
        )
        self.worker.start()

    def _on_reply(self, replies: list, is_error: bool, conv_id: str, run_id: int):
        if self.current_conv_id != conv_id or self.typing_run_id != run_id:
            return

        if is_error:
            self.chat_area.hide_typing()
            self.chat_area.add_message("assistant", replies[0])
            self.displayed_messages.append({"role": "assistant", "content": replies[0]})
            self.input_area.set_enabled(True)
            self.input_area.focus_input()
            return

        self.pending_replies = replies
        self._process_next_reply(run_id)

    def _process_next_reply(self, run_id: int):
        if self.typing_run_id != run_id:
            return

        from PyQt6.QtCore import QTimer
        if not hasattr(self, "pending_replies") or not self.pending_replies:
            self.chat_area.hide_typing()
            self.input_area.set_enabled(True)
            self.input_area.focus_input()

            conv = history.get_conversation(self.current_conv_id)
            if conv:
                self.sidebar.update_conv_title(self.current_conv_id, conv.get("title", "New Chat"))
            self.sidebar.refresh(select_id=self.current_conv_id)
            return

        reply = self.pending_replies.pop(0)
        delay_ms = min(500 + len(reply) * 80, 5000)

        self.chat_area.show_typing()
        QTimer.singleShot(delay_ms, lambda: self._show_reply_and_next(reply, run_id))

    def _show_reply_and_next(self, reply: str, run_id: int):
        if self.typing_run_id != run_id:
            return
            
        self.chat_area.hide_typing()
        self.chat_area.add_message("assistant", reply)
        self.displayed_messages.append({"role": "assistant", "content": reply})
        self._process_next_reply(run_id)

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QMenu, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QAction
from core.config import PROVIDERS


class ChatInputArea(QWidget):
    send_requested = pyqtSignal(str)

    def __init__(self, config_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("input_wrapper")
        self.config_data = config_data
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 14)
        root.setSpacing(4)

        # Main pill row
        pill = QFrame()
        pill.setObjectName("input_pill")
        pill_ly = QHBoxLayout(pill)
        pill_ly.setContentsMargins(14, 4, 6, 4)
        pill_ly.setSpacing(6)

        # Model selector (left, inside pill)
        self.model_btn = QPushButton()
        self.model_btn.setObjectName("model_pill_btn")
        self.model_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.model_btn.clicked.connect(self._show_model_menu)
        self._refresh_model_btn()
        pill_ly.addWidget(self.model_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedHeight(20)
        div.setStyleSheet("background: #2a2d3e; max-width: 1px;")
        pill_ly.addWidget(div, 0, Qt.AlignmentFlag.AlignVCenter)

        # Text input
        self.text_edit = _AutoResizeTextEdit()
        self.text_edit.setObjectName("chat_input")
        self.text_edit.setPlaceholderText("Type a message...")
        self.text_edit.return_pressed.connect(self._on_send)
        pill_ly.addWidget(self.text_edit, 1)

        # Send button (blue circle)
        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self._on_send)
        pill_ly.addWidget(self.send_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        root.addWidget(pill)

        # Hint
        hint = QLabel("Enter to send  ·  Shift+Enter for new line")
        hint.setObjectName("hint_label")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

    def _refresh_model_btn(self):
        m = self.config_data.get("model", "gpt-4o-mini")
        self.model_btn.setText(f"⚡ {m} ▾")

    def _show_model_menu(self):
        provider = self.config_data.get("provider", "OpenAI")
        models   = PROVIDERS.get(provider, {}).get("models", [])
        if not models:
            return
        menu = QMenu(self)
        for m in models:
            act = QAction(m, self)
            act.triggered.connect(lambda checked, model=m: self._set_model(model))
            menu.addAction(act)
        pos = self.model_btn.mapToGlobal(QPoint(0, -menu.sizeHint().height() - 4))
        menu.exec(pos)

    def _set_model(self, model: str):
        self.config_data["model"] = model
        self._refresh_model_btn()

    def update_config(self, config_data: dict):
        self.config_data = config_data
        self._refresh_model_btn()

    def _on_send(self):
        text = self.text_edit.toPlainText().strip()
        if text:
            self.send_requested.emit(text)
            self.text_edit.clear()

    def set_enabled(self, enabled: bool):
        self.text_edit.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)

    def focus_input(self):
        self.text_edit.setFocus()


class _AutoResizeTextEdit(QTextEdit):
    return_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.document().contentsChanged.connect(self._adjust_height)

    def _adjust_height(self):
        h = int(self.document().size().height()) + 16
        self.setFixedHeight(max(38, min(h, 150)))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.return_pressed.emit()
        else:
            super().keyPressEvent(event)

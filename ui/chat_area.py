from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPixmap
from datetime import datetime
from ui.styles import (
    BG_CHAT, BG_BUBBLE_USER, BG_BUBBLE_BOT,
    TEXT_WHITE, TEXT_PRIMARY, TEXT_MUTED, TEXT_SECONDARY,
    ACCENT, ACCENT2, BORDER, BG_ACTIVE
)


def _ai_avatar(size: int = 36) -> QPixmap:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor("#1e2533")))
    p.setPen(QPen(QColor(ACCENT), 1.5))
    p.drawEllipse(2, 2, size - 4, size - 4)
    p.setPen(QPen(QColor(ACCENT)))
    font = p.font()
    font.setPointSize(size // 3)
    font.setBold(True)
    p.setFont(font)
    p.drawText(2, 2, size - 4, size - 4, Qt.AlignmentFlag.AlignCenter, "✦")
    p.end()
    return px


class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_scroll")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(f"QScrollArea#chat_scroll {{ background-color: {BG_CHAT}; border: none; }}")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {BG_CHAT};")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(20, 20, 20, 12)
        self.layout.setSpacing(2)
        self.setWidget(self.container)

        self._typing_widget = None
        self._dots_timer    = None
        self._dots_label    = None
        self._dots_step     = 0

        self._add_welcome()

    def _add_welcome(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        ly = QVBoxLayout(w)
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.setContentsMargins(0, 80, 0, 40)
        ly.setSpacing(12)

        icon = QLabel()
        px = _ai_avatar(64)
        icon.setPixmap(px)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("AI Assistant")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: 800; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub = QLabel("Send a message to start chatting")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        online = QLabel("● Active Now")
        online.setStyleSheet(f"color: #25d366; font-size: 12px; font-weight: 600; background: transparent;")
        online.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ly.addWidget(icon)
        ly.addWidget(title)
        ly.addWidget(online)
        ly.addSpacing(4)
        ly.addWidget(sub)
        self.layout.addWidget(w)

    def _add_date_pill(self, text: str = "Today"):
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        ly = QHBoxLayout(row)
        ly.setContentsMargins(0, 8, 0, 8)
        pill = QLabel(text)
        pill.setObjectName("date_pill")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.addStretch()
        ly.addWidget(pill)
        ly.addStretch()
        self.layout.addWidget(row)

    def clear_chat(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._add_welcome()

    def load_messages(self, messages: list):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not messages:
            self._add_welcome()
            return
        self._add_date_pill("Today")
        for msg in messages:
            if msg["role"] in ("user", "assistant"):
                self._add_bubble(msg["role"], msg["content"])
        self._scroll_to_bottom()

    def add_message(self, role: str, text: str):
        if self.layout.count() == 1:  # only welcome widget
            # Replace welcome with date pill
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            self._add_date_pill("Today")
        self._add_bubble(role, text)
        self._scroll_to_bottom()

    def _add_bubble(self, role: str, text: str):
        is_user = (role == "user")

        outer = QWidget()
        outer.setStyleSheet("background: transparent;")
        outer_ly = QHBoxLayout(outer)
        outer_ly.setContentsMargins(0, 3, 0, 3)
        outer_ly.setSpacing(8)

        if not is_user:
            av = QLabel()
            av.setPixmap(_ai_avatar(36))
            av.setFixedSize(36, 36)
            outer_ly.addWidget(av, 0, Qt.AlignmentFlag.AlignBottom)
        else:
            outer_ly.addStretch()

        bubble = QLabel()
        bubble.setText(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        bubble.setMaximumWidth(500)
        bubble.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        if is_user:
            # User: right side, full rounded except bottom-right
            style = f"""
                QLabel {{
                    background-color: {BG_BUBBLE_USER};
                    color: {TEXT_WHITE};
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    padding: 10px 16px;
                    font-size: 14px;
                    line-height: 1.5;
                }}
            """
        else:
            # Bot: left side, full rounded except bottom-left
            style = f"""
                QLabel {{
                    background-color: {BG_BUBBLE_BOT};
                    color: {TEXT_PRIMARY};
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                    padding: 10px 16px;
                    font-size: 14px;
                    line-height: 1.5;
                }}
            """
        bubble.setStyleSheet(style)
        outer_ly.addWidget(bubble, 0, Qt.AlignmentFlag.AlignBottom)

        if is_user:
            pass  # no stretch after user bubble
        else:
            outer_ly.addStretch()

        self.layout.addWidget(outer)

    def show_typing(self):
        self._typing_widget = QWidget()
        self._typing_widget.setStyleSheet("background: transparent;")
        ly = QHBoxLayout(self._typing_widget)
        ly.setContentsMargins(0, 3, 0, 3)
        ly.setSpacing(8)

        av = QLabel()
        av.setPixmap(_ai_avatar(36))
        av.setFixedSize(36, 36)
        ly.addWidget(av, 0, Qt.AlignmentFlag.AlignBottom)

        self._dots_label = QLabel("●  ●  ●")
        self._dots_label.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_BUBBLE_BOT};
                color: {ACCENT};
                border-radius: 18px;
                border-bottom-left-radius: 4px;
                padding: 12px 20px;
                font-size: 14px;
            }}
        """)
        ly.addWidget(self._dots_label, 0, Qt.AlignmentFlag.AlignBottom)
        ly.addStretch()

        self.layout.addWidget(self._typing_widget)
        self._scroll_to_bottom()

        self._dots_step  = 0
        self._dots_timer = QTimer(self)
        self._dots_timer.timeout.connect(self._animate_dots)
        self._dots_timer.start(350)

    def _animate_dots(self):
        frames = ["●  ○  ○", "●  ●  ○", "●  ●  ●", "○  ●  ●", "○  ○  ●"]
        if self._dots_label:
            self._dots_label.setText(frames[self._dots_step % len(frames)])
        self._dots_step += 1

    def hide_typing(self):
        if self._dots_timer:
            self._dots_timer.stop()
            self._dots_timer = None
        if self._typing_widget:
            self._typing_widget.deleteLater()
            self._typing_widget = None
        self._dots_label = None

    def _scroll_to_bottom(self):
        QTimer.singleShot(60, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))

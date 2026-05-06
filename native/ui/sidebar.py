from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPixmap
from datetime import datetime
from native.api_client import APIClient
from native.ui.styles import (
    BG_ACTIVE, BG_SIDEBAR_HOV, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, ACCENT, BORDER, SUCCESS
)


def _avatar_pixmap(letter: str, size: int = 40, color: str = "#4f6ef7") -> QPixmap:
    """Create a circular avatar with an initial letter."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, size, size)
    p.setPen(QPen(QColor("#ffffff")))
    font = p.font()
    font.setPointSize(size // 3)
    font.setBold(True)
    p.setFont(font)
    p.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, letter.upper())
    p.end()
    return px


class ConvItem(QFrame):
    clicked = pyqtSignal(str)
    deleted = pyqtSignal(str)

    _AVATAR_COLORS = [
        "#4f6ef7", "#e05678", "#25a56a", "#f07d3e",
        "#9b59b6", "#1abc9c", "#e74c3c", "#3498db"
    ]

    def __init__(self, conv: dict, is_active: bool = False, index: int = 0, parent=None):
        super().__init__(parent)
        self.conv_id = conv["id"]
        self._is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(is_active)

        ly = QHBoxLayout(self)
        ly.setContentsMargins(10, 8, 8, 8)
        ly.setSpacing(10)

        # Avatar
        color = self._AVATAR_COLORS[index % len(self._AVATAR_COLORS)]
        title = conv.get("title", "New Chat")
        letter = title[0] if title else "N"
        av_lbl = QLabel()
        av_lbl.setPixmap(_avatar_pixmap(letter, 42, color))
        av_lbl.setFixedSize(42, 42)
        ly.addWidget(av_lbl)

        # Text info
        info = QVBoxLayout()
        info.setSpacing(3)
        info.setContentsMargins(0, 0, 0, 0)

        self.name_lbl = QLabel(title[:30])
        self.name_lbl.setObjectName("conv_name")

        # Use last message as preview if available
        msgs = conv.get("messages", [])
        if msgs:
            last = msgs[-1]
            preview = last.get("content", "")[:35]
            prefix = "You: " if last.get("role") == "user" else "AI: "
        else:
            preview = "New conversation"
            prefix = ""
        self.prev_lbl = QLabel(prefix + preview)
        self.prev_lbl.setObjectName("conv_preview")

        info.addWidget(self.name_lbl)
        info.addWidget(self.prev_lbl)
        ly.addLayout(info, 1)

        # Right side: time + delete
        right = QVBoxLayout()
        right.setSpacing(4)
        right.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        ts_raw = conv.get("updated_at", "")
        try:
            ts = datetime.fromisoformat(ts_raw).strftime("%H:%M")
        except Exception:
            ts = ""
        time_lbl = QLabel(ts)
        time_lbl.setObjectName("conv_time")
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.del_btn = QPushButton("✕")
        self.del_btn.setObjectName("delete_btn")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.hide()
        self.del_btn.clicked.connect(lambda: self.deleted.emit(self.conv_id))

        right.addWidget(time_lbl)
        right.addWidget(self.del_btn, 0, Qt.AlignmentFlag.AlignRight)
        ly.addLayout(right)

    def _apply_style(self, active: bool):
        self.setObjectName("conv_item_active" if active else "conv_item")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool):
        self._is_active = active
        self._apply_style(active)

    def update_title(self, title: str):
        self.name_lbl.setText(title[:30])

    def enterEvent(self, e):
        self.del_btn.show()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.del_btn.hide()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.conv_id)
        super().mousePressEvent(e)


class Sidebar(QWidget):
    conv_selected = pyqtSignal(str)
    new_chat      = pyqtSignal()
    open_settings = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self._items: dict[str, ConvItem] = {}
        self._active_id: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 16, 10, 10)
        root.setSpacing(8)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("Chats")
        title.setObjectName("sidebar_title")
        new_btn = QPushButton("✎")
        new_btn.setObjectName("new_conv_btn")
        new_btn.setToolTip("New Chat")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.new_chat)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(new_btn)
        root.addLayout(title_row)

        # Search
        self.search = QLineEdit()
        self.search.setObjectName("search_box")
        self.search.setPlaceholderText("🔍   Search Messenger")
        self.search.textChanged.connect(self._filter)
        root.addWidget(self.search)

        # Scroll area for convs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(2)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.list_widget)
        root.addWidget(scroll, 1)

        # Settings button at bottom
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {BORDER}; max-height: 1px;")
        root.addWidget(sep)

        settings_btn = QPushButton("⚙   Settings")
        settings_btn.setObjectName("sidebar_action_btn")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)
        root.addWidget(settings_btn)

        self.refresh()

    def refresh(self, select_id: str | None = None):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._items.clear()

        convs = APIClient.list_conversations()
        active = select_id or self._active_id

        for i, conv in enumerate(convs):
            item = ConvItem(conv, is_active=(conv["id"] == active), index=i)
            item.clicked.connect(self._on_item_clicked)
            item.deleted.connect(self._on_item_deleted)
            self.list_layout.addWidget(item)
            self._items[conv["id"]] = item

        self._active_id = active

    def set_active(self, conv_id: str):
        self._active_id = conv_id
        for cid, item in self._items.items():
            item.set_active(cid == conv_id)

    def update_conv_title(self, conv_id: str, title: str):
        if conv_id in self._items:
            self._items[conv_id].update_title(title)

    def _on_item_clicked(self, conv_id: str):
        self.set_active(conv_id)
        self.conv_selected.emit(conv_id)

    def _on_item_deleted(self, conv_id: str):
        APIClient.delete_conversation(conv_id)
        was_active = (conv_id == self._active_id)
        self._active_id = None
        self.refresh()
        if was_active:
            self.new_chat.emit()

    def _filter(self, text: str):
        text = text.lower()
        for _, item in self._items.items():
            item.setVisible(text in item.name_lbl.text().lower())

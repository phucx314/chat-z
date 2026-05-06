from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt



class SettingsDialog(QDialog):
    def __init__(self, config_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(460)
        self.config_data = config_data.copy()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 24)
        root.setSpacing(20)

        providers = self.config_data.get("providers", {})

        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #e4e6eb;")
        root.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #3e4042; max-height: 1px;")
        root.addWidget(line)

        # Provider
        root.addWidget(self._section_label("Provider"))
        self.provider_cb = QComboBox()
        self.provider_cb.addItems(list(providers.keys()))
        self.provider_cb.setCurrentText(self.config_data.get("provider", "OpenAI"))
        self.provider_cb.currentTextChanged.connect(self._on_provider_changed)
        root.addWidget(self.provider_cb)

        # API Key
        root.addWidget(self._section_label("API Key"))
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setPlaceholderText("Nhập API key (để trống nếu dùng .env)")
        # Never pre-fill with env key — intentionally blank
        self.api_input.setText(self.config_data.get("api_key", ""))
        root.addWidget(self.api_input)

        # Env key indicator (informational only, no value shown)
        if self.config_data.get("_key_from_env"):
            info = QLabel("✓ Key đang được load từ file .env")
            info.setStyleSheet("color: #42b883; font-size: 12px;")
            root.addWidget(info)

        # Base URL
        root.addWidget(self._section_label("Base URL"))
        self.base_input = QLineEdit()
        self.base_input.setText(
            self.config_data.get("base_url") or
            providers.get(self.config_data.get("provider", "OpenAI"), {}).get("base_url", "")
        )
        root.addWidget(self.base_input)

        # Behavior
        from PyQt6.QtWidgets import QCheckBox
        self.interrupt_cb = QCheckBox("Cho phép Chat Chen Ngang (Dừng AI đang gõ)")
        self.interrupt_cb.setStyleSheet("color: #e4e6eb; font-size: 13px;")
        self.interrupt_cb.setChecked(self.config_data.get("allow_interrupt", False))
        root.addWidget(self.interrupt_cb)

        root.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        save = QPushButton("Save")
        save.setObjectName("dialog_primary")
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.clicked.connect(self._save)

        cancel = QPushButton("Cancel")
        cancel.setObjectName("dialog_cancel")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setStyleSheet("color: #65676b; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")
        return lbl

    def _on_provider_changed(self, provider: str):
        providers = self.config_data.get("providers", {})
        preset = providers.get(provider, {})
        self.base_input.setText(preset.get("base_url", ""))

    def _save(self):
        self.config_data["provider"] = self.provider_cb.currentText()
        self.config_data["api_key"]  = self.api_input.text().strip()  # manually entered only
        self.config_data["base_url"] = self.base_input.text().strip()
        self.config_data["allow_interrupt"] = self.interrupt_cb.isChecked()
        self.accept()

    def get_config(self) -> dict:
        return self.config_data

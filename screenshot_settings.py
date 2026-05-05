import sys
from PyQt6.QtWidgets import QApplication
from ui.settings_dialog import SettingsDialog
from ui.styles import GLOBAL_STYLE

app = QApplication(sys.argv)
app.setStyleSheet(GLOBAL_STYLE)
# dummy config
config = {"provider": "OpenAI", "api_key": "123", "base_url": "", "model": "gpt-4", "system_prompt": "hello", "_key_from_env": True}
dlg = SettingsDialog(config)
dlg.show()

# take screenshot after 100ms
from PyQt6.QtCore import QTimer
def take_ss():
    pixmap = dlg.grab()
    pixmap.save("settings_ss.png")
    app.quit()

QTimer.singleShot(100, take_ss)
app.exec()

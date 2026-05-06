import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from native.ui.main_window import MainWindow
from native.ui.styles import GLOBAL_STYLE

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

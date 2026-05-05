import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import GLOBAL_STYLE

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

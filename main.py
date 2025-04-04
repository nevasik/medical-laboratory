import sys
from ui.login_window import LoginWindow
from PyQt6.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
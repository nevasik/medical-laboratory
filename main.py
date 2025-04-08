import sys
from PyQt6.QtWidgets import QApplication
from order_window import OrderWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderWindow()
    window.show()
    sys.exit(app.exec())
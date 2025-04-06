from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

from quality_control_report import QualityControlReport
from service_report_widget import ServiceReportWidget


class MainWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Медицинская лаборатория - Отчеты")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Стиль для кнопок
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        # Кнопка отчета по контролю качества
        btn_quality = QPushButton("Контроль качества")
        btn_quality.setStyleSheet(button_style)
        btn_quality.clicked.connect(self.show_quality_report)

        # Кнопка отчета по услугам
        btn_service = QPushButton("Отчет по услугам")
        btn_service.setStyleSheet(button_style)
        btn_service.clicked.connect(self.show_service_report)

        # Кнопка выхода
        btn_exit = QPushButton("Выход")
        btn_exit.setStyleSheet(button_style.replace("#4CAF50", "#f44336"))
        btn_exit.clicked.connect(self.close)

        # Добавляем элементы в layout
        title = QLabel("Выберите тип отчета:")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 30px;")

        layout.addWidget(title)
        layout.addWidget(btn_quality)
        layout.addWidget(btn_service)
        layout.addWidget(btn_exit)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_quality_report(self):
        self.report = QualityControlReport(self.connection)
        self.report.show()

    def show_service_report(self):
        self.report = ServiceReportWidget(self.connection)
        self.report.show()

    def closeEvent(self, event):
        # Закрываем соединение с БД при закрытии приложения
        if self.connection and self.connection.open:
            self.connection.close()
        event.accept()
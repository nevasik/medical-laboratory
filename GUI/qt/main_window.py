from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt

from GUI.qt.quality_control_report import QualityControlReport
from GUI.qt.service_report_widget import ServiceReportWidget
from utils.style import BUTTON_STYLE, LABEL_STYLE, MAIN_WINDOW_STYLE


class MainWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Медицинская лаборатория - Отчеты")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Кнопка отчета по контролю качества
        btn_quality = QPushButton("Контроль качества")
        btn_quality.setStyleSheet(BUTTON_STYLE)
        btn_quality.clicked.connect(self.show_quality_report)

        # Кнопка отчета по услугам
        btn_service = QPushButton("Отчет по услугам")
        btn_service.setStyleSheet(BUTTON_STYLE)
        btn_service.clicked.connect(self.show_service_report)

        # Кнопка выхода
        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(self.close)

        # Добавляем элементы в layout
        title = QLabel("Выберите тип отчета:")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(LABEL_STYLE)

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
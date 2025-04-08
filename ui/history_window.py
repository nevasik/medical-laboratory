from database import connection, queries
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QHeaderView, QLabel
)
from ui.models import HistoryModel
from PyQt6.QtGui import QPixmap, QIcon
from styles import COMMON_STYLE
from PyQt6.QtCore import Qt


class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История входов")
        self.setGeometry(100, 100, 800, 600)
        self._init_ui()
        self._connect_signals()

        self.setWindowIcon(QIcon('resources/logo.ico'))

    def _init_ui(self):
        layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap('resources/logo.png').scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        layout.insertWidget(0, logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        filter_layout = QHBoxLayout()
        
        self.login_filter = QLineEdit(placeholderText="Фильтр по логину")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сначала новые", "Сначала старые"])
        self.apply_btn = QPushButton("Применить")
        
        filter_layout.addWidget(self.login_filter)
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(self.apply_btn)
        layout.addLayout(filter_layout)

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        self.close_btn = QPushButton("Закрыть")
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.load_data()

        self.setStyleSheet(COMMON_STYLE)

    def _connect_signals(self):
        self.apply_btn.clicked.connect(self.load_data)
        self.close_btn.clicked.connect(self.close)

    def load_data(self):
        """Загружает данные истории входов с учетом фильтров"""
        login_filter = self.login_filter.text()
        sort_order = "DESC" if self.sort_combo.currentIndex() == 0 else "ASC"

        conn = None
        try:
            conn = connection.get_connection()
            cursor = conn.cursor()

            query = queries.QUERIES['get_history'].format(sort_order=sort_order)
            cursor.execute(query, (f"%{login_filter}%",))
            results = cursor.fetchall()

            self.model = HistoryModel(results)
            self.table.setModel(self.model)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
        finally:
            if conn and conn.open:
                cursor.close()
                conn.close()
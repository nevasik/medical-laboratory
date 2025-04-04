from database import connection, queries
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QHeaderView
)
from ui.models import HistoryModel


class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История входов")
        self.setGeometry(100, 100, 800, 600)
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Filter and sort controls
        filter_layout = QHBoxLayout()
        
        self.login_filter = QLineEdit(placeholderText="Фильтр по логину")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сначала новые", "Сначала старые"])
        self.apply_btn = QPushButton("Применить")
        
        filter_layout.addWidget(self.login_filter)
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(self.apply_btn)
        layout.addLayout(filter_layout)

        # Table view
        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        # Close button
        self.close_btn = QPushButton("Закрыть")
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        self.load_data()

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
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
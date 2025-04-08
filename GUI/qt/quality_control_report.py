import numpy as np
import pymysql
from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, QDateEdit,
                             QComboBox, QMessageBox, QDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from GUI.qt.service_report_widget import ServiceReportWidget


class QualityControlReport(QDialog):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.setWindowTitle("Контроль качества")
        self.setGeometry(200, 200, 1200, 800)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        control_layout = QHBoxLayout()

        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-30))
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDateTime(QDateTime.currentDateTime())

        self.equipment_combo = QComboBox()
        self.load_equipment()

        self.btn_generate = QPushButton("Сформировать отчёт")
        self.btn_generate.clicked.connect(self.generate_report)

        # btn_service = QPushButton("Отчёт по услугам")
        # btn_service.clicked.connect(self.show_service_report)

        control_layout.addWidget(QLabel("Оборудование:"))
        control_layout.addWidget(self.equipment_combo)
        control_layout.addWidget(QLabel("С:"))
        control_layout.addWidget(self.date_from)
        control_layout.addWidget(QLabel("По:"))
        control_layout.addWidget(self.date_to)
        control_layout.addWidget(self.btn_generate)
        # layout.addWidget(btn_service)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Дата",
            "Значение",
            "Среднее (X̄)",
            "Отклонение"
        ])

        layout.addLayout(control_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_equipment(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT equipment_id, equipment_name FROM equipment")
                for row in cursor.fetchall():
                    self.equipment_combo.addItem(
                        row['equipment_name'],  # Отображаемое имя
                        userData=row['equipment_id']  # Скрытый ID
                    )
        except pymysql.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки оборудования: {e}")

    def generate_report(self):
        equipment_id = self.equipment_combo.currentData()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")

        if not equipment_id:
            QMessageBox.warning(self, "Ошибка", "Не выбрано оборудование")
            return

        try:
            with self.connection.cursor() as cursor:  # Используем контекстный менеджер
                query = """
                    SELECT test_value, test_date 
                    FROM quality_control 
                    WHERE equipment_id = %s 
                        AND test_date BETWEEN %s AND %s
                    ORDER BY test_date
                """

                cursor.execute(query, (equipment_id, date_from, date_to))
                data = cursor.fetchall()

                if not data:
                    QMessageBox.warning(self, "Предупреждение", "Нет данных для выбранного периода")
                    return

                # Преобразуем все значения к float
            values = [float(row['test_value']) for row in data]  # Явное преобразование
            dates = [row['test_date'] for row in data]

            mean = np.mean(values)
            std = np.std(values)
            cv = (std / mean) * 100 if mean != 0 else 0

            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                value = float(row['test_value'])  # Преобразуем здесь
                date = row['test_date']

                self.table.setItem(row_idx, 0, QTableWidgetItem(str(date)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(f"{value:.2f}"))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{mean:.2f}"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(f"{(value - mean):.2f}"))  # Теперь оба float

                # Остальная часть кода с графиком без изменений
                self.figure.clear()
                ax = self.figure.add_subplot(111)

                limits = {
                    '+3S': mean + 3 * std,
                    '+2S': mean + 2 * std,
                    '+1S': mean + 1 * std,
                    'X̄': mean,
                    '-1S': mean - 1 * std,
                    '-2S': mean - 2 * std,
                    '-3S': mean - 3 * std
                }

                colors = {
                    '±3S': 'red',
                    '±2S': 'orange',
                    '±1S': 'yellow',
                    'X̄': 'green'
                }

                for label, value in limits.items():
                    color = colors.get(label.replace('+', '±').replace('-', '±'), 'gray')
                    ax.axhline(y=value, color=color, linestyle='--', label=label)

                ax.plot(dates, values, 'bo-', label='Измерения')

                ax.set_title(f"Контроль качества оборудования: {self.equipment_combo.currentText()}\n"
                             f"X̄ = {mean:.2f}, SD = {std:.2f}, CV = {cv:.2f}%")
                ax.set_xlabel("Дата и время исследования")
                ax.set_ylabel("Значение измерения")
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                self.canvas.draw()

        except pymysql.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Непредвиденная ошибка: {str(e)}")


def show_service_report(self):
    self.report = ServiceReportWidget(self.connection)
    self.report.show()

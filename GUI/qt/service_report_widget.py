import tempfile

import numpy as np
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table

from utils.style import TABLE_STYLE, BUTTON_STYLE


class ServiceReportWidget(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.initUI()
        self.current_data = None
        self.current_layout = 'table'

    def initUI(self):
        self.layout = QVBoxLayout()

        # Панель управления
        control_layout = QHBoxLayout()

        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())

        self.view_combo = QComboBox()
        self.view_combo.addItems(["Таблица", "График", "Оба"])

        self.btn_generate = QPushButton("Сформировать")
        self.btn_generate.clicked.connect(self.generate_report)
        self.btn_generate.setStyleSheet(BUTTON_STYLE)

        self.btn_export = QPushButton("Экспорт в PDF")
        self.btn_export.clicked.connect(self.export_to_pdf)
        self.btn_export.setStyleSheet(BUTTON_STYLE)

        control_layout.addWidget(QLabel("С:"))
        control_layout.addWidget(self.start_date)
        control_layout.addWidget(QLabel("По:"))
        control_layout.addWidget(self.end_date)
        control_layout.addWidget(QLabel("Вид:"))
        control_layout.addWidget(self.view_combo)
        control_layout.addWidget(self.btn_generate)
        control_layout.addWidget(self.btn_export)

        # Контейнер для контента
        self.content_layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Дата",
            "Услуга",
            "Кол-во пациентов",
            "Средний результат",
            "Всего за день"
        ])

        # График
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addLayout(control_layout)
        self.layout.addLayout(self.content_layout)
        self.setLayout(self.layout)

    def generate_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT 
                    DATE(qc.test_date) as date,
                    c.service_type,
                    COUNT(DISTINCT a.appointment_id) as patients,
                    AVG(qc.test_value) as avg_value,
                    COUNT(*) as total
                FROM quality_control qc
                JOIN appointment a ON qc.appointment_id = a.appointment_id
                JOIN contract c ON a.contract_id = c.contract_id
                WHERE DATE(qc.test_date) BETWEEN %s AND %s
                GROUP BY DATE(qc.test_date), c.service_type
                ORDER BY date
                """
                cursor.execute(query, (start, end))
                self.current_data = cursor.fetchall()

            if not self.current_data:
                QMessageBox.warning(self, "Нет данных", "Нет данных за выбранный период")
                return

            self.update_view()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_view(self):
        # Очищаем предыдущий контент
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

        view_type = self.view_combo.currentText()

        if view_type in ["Таблица", "Оба"]:
            self.update_table()

        if view_type in ["График", "Оба"]:
            self.update_chart()

    def update_table(self):
        self.table.setRowCount(len(self.current_data))
        for row_idx, row in enumerate(self.current_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['date'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['service_type']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['patients'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row['avg_value']:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row['total'])))
        self.content_layout.addWidget(self.table)

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        dates = sorted(set(row['date'] for row in self.current_data))
        services = sorted(set(row['service_type'] for row in self.current_data))

        # Подготовка данных
        data = {service: [] for service in services}
        for date in dates:
            for service in services:
                count = next((row['patients'] for row in self.current_data
                              if row['date'] == date and row['service_type'] == service), 0)
                data[service].append(count)

        # Построение графика
        bottom = np.zeros(len(dates))
        for service, counts in data.items():
            ax.bar(dates, counts, label=service, bottom=bottom)
            bottom += np.array(counts)

        ax.set_title("Количество пациентов по услугам")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество пациентов")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=45)

        self.canvas.draw()
        self.content_layout.addWidget(self.canvas)

    def export_to_pdf(self):
        if not self.current_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return

        # Исправленная часть: используем флаги напрямую без объекта Options
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_name:
            return

        # Добавляем расширение .pdf, если его нет
        if not file_name.endswith('.pdf'):
            file_name += '.pdf'

        # Создаем временные файлы для графиков
        with tempfile.TemporaryDirectory() as tmpdir:
            # Сохраняем графики
            chart_path = f"{tmpdir}/chart.png"
            self.figure.savefig(chart_path, bbox_inches='tight')

            # Создаем PDF
            pdf = canvas.Canvas(file_name, pagesize=A4)
            width, height = A4

            # Добавляем таблицу
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, height - 50,
                           f"Отчет по услугам с {self.start_date.date().toString()} по {self.end_date.date().toString()}")

            # Подготовка данных для таблицы
            table_data = [["Дата", "Услуга", "Пациенты", "Средний результат", "Всего"]]
            for row in self.current_data:
                table_data.append([
                    str(row.get('date', '')),
                    str(row.get('service_type', '')),
                    str(row.get('patients', 0)),
                    f"{row.get('avg_value', 0):.2f}",
                    str(row.get('total', 0))
                ])

            # Создаем таблицу
            t = Table(table_data)


            # Рассчитываем размеры
            available_width = width - 100
            col_widths = [available_width * 0.2, 0.3, 0.15, 0.2, 0.15]
            t._argW = [w * available_width for w in col_widths]

            # Добавляем таблицу в PDF
            t.wrapOn(pdf, width, height)
            t.drawOn(pdf, 50, height - 250)

            # Добавляем график
            pdf.drawImage(chart_path, 50, height - 550, width=500, preserveAspectRatio=True)

            pdf.save()

        QMessageBox.information(self, "Успех", "PDF успешно экспортирован")

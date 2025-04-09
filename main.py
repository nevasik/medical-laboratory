import os
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from report.generate_pdf_report import generate_pdf_report

# Стили
from styles import MAIN_WINDOW_STYLE, BUTTON_STYLE, LABEL_STYLE

API_URL = "http://localhost:5000/api/analyzer"
PATIENT_ID = "P123"
SELECTED_ANALYZER = "Ledetect"

# Локальные доступные услуги
SERVICES = [
    {"code": 619, "name": "TSH"},
    {"code": 311, "name": "Амилаза"},
    {"code": 501, "name": "Гепатит В"},
]


class PollingThread(QThread):
    progress_updated = pyqtSignal(int)
    result_received = pyqtSignal(list)

    def run(self):
        while True:
            try:
                res = requests.get(f"{API_URL}/{SELECTED_ANALYZER}", params={"patient": PATIENT_ID})
                data = res.json()
                if "progress" in data:
                    self.progress_updated.emit(data["progress"])
                    self.sleep(1)
                else:
                    self.result_received.emit(data["services"])
                    break
            except Exception as e:
                print("❌ Ошибка при опросе анализатора:", e)
                break


class AnalyzerClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализатор")
        self.setGeometry(100, 100, 420, 360)
        self.setStyleSheet(MAIN_WINDOW_STYLE + BUTTON_STYLE + LABEL_STYLE)

        layout = QVBoxLayout()

        self.label = QLabel("Выберите услугу:")
        layout.addWidget(self.label)

        self.service_list = QListWidget()
        for s in SERVICES:
            self.service_list.addItem(f"{s['code']} - {s['name']}")
        layout.addWidget(self.service_list)

        self.send_button = QPushButton("Отправить на исследование")
        self.send_button.clicked.connect(self.send_to_analyzer)
        layout.addWidget(self.send_button)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.result_label = QLabel("Результат: ---")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label)

        self.approve_button = QPushButton("Одобрить")
        self.approve_button.setEnabled(False)
        self.approve_button.clicked.connect(self.approve_result)
        layout.addWidget(self.approve_button)

        self.setLayout(layout)

    def send_to_analyzer(self):
        index = self.service_list.currentRow()
        if index == -1:
            QMessageBox.warning(self, "Внимание", "Выберите услугу перед отправкой.")
            return

        service_code = SERVICES[index]["code"]
        try:
            resp = requests.post(
                f"{API_URL}/{SELECTED_ANALYZER}",
                json={"patient": PATIENT_ID, "services": [{"serviceCode": service_code}]}
            )
            if resp.status_code == 200:
                self.progress.setValue(0)
                self.result_label.setText("Ожидание результата...")
                self.approve_button.setEnabled(False)

                self.thread = PollingThread()
                self.thread.progress_updated.connect(self.progress.setValue)
                self.thread.result_received.connect(self.show_result)
                self.thread.start()
            else:
                QMessageBox.critical(self, "Ошибка", resp.json().get("detail", "Неизвестная ошибка"))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_result(self, services):
        try:
            print("📦 Полученные результаты:", services)

            generate_pdf_report(
                PATIENT_ID,
                services,
                save_path=os.path.abspath("reports")
            )

            result = str(services[0].get("result", "Нет данных"))
            self.result_label.setText(f"Результат: {result}")
            self.approve_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчёта: {str(e)}")

    def approve_result(self):
        QMessageBox.information(self, "Успех", "Результат одобрен!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = AnalyzerClient()
    client.show()
    sys.exit(app.exec())

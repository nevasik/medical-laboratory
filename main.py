import os
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal

from report.generate_pdf_report import generate_pdf_report

API_URL = "http://localhost:5000/api/analyzer"

# Константы
PATIENT_ID = "P123"
SELECTED_ANALYZER = "Ledetect"
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
                print("Error polling:", e)
                break

class AnalyzerClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализатор")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.service_list = QListWidget()
        for s in SERVICES:
            self.service_list.addItem(f"{s['code']} - {s['name']}")
        layout.addWidget(QLabel("Выберите услугу:"))
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
                QMessageBox.critical(self, "Ошибка", resp.json()["detail"])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    # В методе show_result (client)

    def show_result(self, services):
        try:
            generate_pdf_report(
                PATIENT_ID,
                services,
                save_path=os.path.abspath("reports")  # Используем абсолютный путь
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации: {str(e)}")



    def approve_result(self):
        QMessageBox.information(self, "Успех", "Результат одобрен!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = AnalyzerClient()
    client.show()
    sys.exit(app.exec())

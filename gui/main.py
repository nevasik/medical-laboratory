import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QProgressBar
import requests
from threading import Thread
import time

class AnalyzerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализаторы")
        self.layout = QVBoxLayout()
        self.analyzers = ["Ledetect", "Biorad"]
        self.analyzer_list = QListWidget()
        self.analyzer_list.addItems(self.analyzers)
        self.layout.addWidget(self.analyzer_list)

        self.order_button = QPushButton("Отправить на исследование")
        self.order_button.clicked.connect(self.send_to_analyzer)
        self.layout.addWidget(self.order_button)

        self.status_label = QLabel("Статус: Ожидание")
        self.layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

    def send_to_analyzer(self):
        analyzer = self.analyzer_list.currentItem().text()
        patient = "12345"
        services = [{"serviceCode": 619}]
        self.status_label.setText(f"Отправлено на {analyzer}")
        Thread(target=self.monitor, args=(analyzer, patient, services)).start()

    def monitor(self, analyzer, patient, services):
        url = f"http://localhost:5000/api/analyzer/{analyzer}"
        try:
            requests.post(url, json={"patient": patient, "services": services})
        except Exception as e:
            self.status_label.setText(f"Ошибка: {str(e)}")
            return
        while True:
            time.sleep(2)
            try:
                res = requests.get(url).json()
                if "progress" in res:
                    self.progress.setValue(res["progress"])
                else:
                    self.status_label.setText(f"Результат: {res['services'][0]['result']}")
                    break
            except Exception as e:
                self.status_label.setText("Ошибка при получении данных")
                break

app = QApplication(sys.argv)
win = AnalyzerWindow()
win.show()
sys.exit(app.exec())

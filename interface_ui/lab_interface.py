from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QProgressBar,
    QMessageBox, QComboBox, QLineEdit, QListWidgetItem, QApplication, QAbstractItemView
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import requests
import sys
from fastapi import FastAPI
from backend.routes.analyzers import router
from backend.services.analyzer_service import REFERENCE_VALUES


app = FastAPI()
app.include_router(router, prefix="/api")


class AnalyzerWorker(QThread):
    update_progress = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, analyzer_name, patient_id, services):
        super().__init__()
        self.analyzer_name = analyzer_name
        self.patient_id = patient_id
        self.services = services

    def run(self):
        try:
            response = requests.post(
                f"http://localhost:8000/api/analyzer/{self.analyzer_name}",
                json={"patient": self.patient_id, "services": self.services}
            )

            while True:
                status = requests.get(
                    f"http://localhost:8000/api/analyzer/{self.analyzer_name}"
                ).json()

                self.update_progress.emit(status)
                if 'progress' not in status or status.get('progress', 100) == 100:
                    break
                self.sleep(1)

        except Exception as e:
            print(f"Ошибка: {str(e)}")
        finally:
            self.finished.emit()


class ServiceItemWidget(QWidget):
    def __init__(self, service):
        super().__init__()
        layout = QHBoxLayout()

        self.service_label = QLabel(f"{service['code']} - {service['name']}")
        self.progress = QProgressBar()
        self.result_edit = QLineEdit()
        self.approve_btn = QPushButton("Подтвердить")

        self.approve_btn.clicked.connect(lambda: self.approve_service(service, self.result_edit))

        layout.addWidget(self.service_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.result_edit)
        layout.addWidget(self.approve_btn)

        self.setLayout(layout)


class AnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Интерфейс лабораторного анализатора")
        self.setGeometry(100, 100, 800, 600)
        self.analyzers = self.load_analyzers()
        self.current_analyzer = None
        self.workers = []
        self.init_ui()
        self.load_pending_services()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Выбор анализатора
        self.analyzer_combo = QComboBox()
        self.analyzer_combo.addItems([a['name'] for a in self.analyzers])
        self.analyzer_combo.currentIndexChanged.connect(self.on_analyzer_changed)
        layout.addWidget(QLabel("Выберите анализатор:"))
        layout.addWidget(self.analyzer_combo)

        # Список услуг
        layout.addWidget(QLabel("Ожидающие исследования:"))
        self.service_list = QListWidget()
        self.service_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.service_list.itemDoubleClicked.connect(self.on_item_double_click)
        layout.addWidget(self.service_list)

        # Управление
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Запустить выбранное исследование")
        self.start_btn.clicked.connect(self.on_start_processing)
        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.load_pending_services)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def load_analyzers(self):
        try:
            response = requests.get("http://localhost:8000/api/analyzers")
            return response.json()
        except:
            return [{"name": "Ledetect"}, {"name": "Biorad"}]

    def load_pending_services(self):
        self.service_list.clear()
        try:
            response = requests.get(
                f"http://localhost:8000/api/services",
                params={
                    "status": "pending",
                    "analyzer": self.current_analyzer
                }
            )
            if response.status_code == 200:
                for service in response.json():
                    item = QListWidgetItem()
                    widget = ServiceItemWidget(service)
                    item.setSizeHint(widget.sizeHint())
                    item.setData(Qt.ItemDataRole.UserRole, service)
                    self.service_list.addItem(item)
                    self.service_list.setItemWidget(item, widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки услуг: {str(e)}")

    def on_analyzer_changed(self):
        self.current_analyzer = self.analyzer_combo.currentText()
        self.load_pending_services()

    def on_item_double_click(self, item):
        self.start_processing(item.data(Qt.ItemDataRole.UserRole))

    def on_start_processing(self):
        selected_items = self.service_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы одну услугу!")
            return

        for item in selected_items:
            service = item.data(Qt.ItemDataRole.UserRole)
            self.start_processing(service)

    def start_processing(self, service):
        if self.current_analyzer in [w.analyzer_name for w in self.workers]:
            QMessageBox.warning(self, "Занят", "Анализатор в настоящее время занят!")
            return

        worker = AnalyzerWorker(
            self.current_analyzer,
            service['patient_id'],
            [{"serviceCode": service['code']}]
        )
        worker.update_progress.connect(self.update_service_status)
        worker.finished.connect(lambda: self.on_processing_finished(worker))
        self.workers.append(worker)
        for w in self.workers:
            if w.analyzer_name == self.current_analyzer and w.patient_id == service['patient_id']:
                QMessageBox.warning(self, "Занят", "Этот анализатор уже работает с данным пациентом!")
                return
        worker.start()

    def update_service_status(self, status):
        for i in range(self.service_list.count()):
            item = self.service_list.item(i)
            widget = self.service_list.itemWidget(item)
            service = item.data(Qt.ItemDataRole.UserRole)

            for s in status.get('services', []):
                if s['code'] == service['code']:
                    result = s.get('result')
                    if result is not None:
                        widget.result_edit.setText(str(result))
                        widget.progress.setValue(100)
                    else:
                        widget.progress.setValue(status.get('progress', 0))

    def update_service_status_backend(self, patient_id, code, status):
        try:
            requests.post("http://localhost:8000/api/service/update_status", json={
                "patient_id": patient_id,
                "service_code": code,
                "status": status
            })
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")

    def approve_service(self, service, result_widget):
        try:
            result = result_widget.text()
            code = service['code']
            ref = REFERENCE_VALUES.get(code)

            warning = False
            if isinstance(ref, (int, float)):
                deviation = abs((float(result) - ref) / ref)
                warning = deviation >= 5

            if warning:
                msg = QMessageBox.warning(None, "Предупреждение",
                                          "Результат сильно отклоняется от нормы! Возможно, сбой анализа. Подтвердить?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if msg == QMessageBox.StandardButton.No:
                    self.update_service_status_backend(service['patient_id'], code, "recollect")
                    return

            self.update_service_status_backend(service['patient_id'], code, "completed")

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка при подтверждении: {str(e)}")

    def on_processing_finished(self, worker):
        self.workers.remove(worker)
        self.load_pending_services()
        QMessageBox.information(self, "Завершено", "Обработка завершена!")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow()
    window.show()
    sys.exit(app.exec())
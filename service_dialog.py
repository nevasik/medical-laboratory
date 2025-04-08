from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QPushButton)
from PyQt6.QtCore import Qt
from database.db import get_services
from logger import logger
from styles import *  # Импортируем все стили

class ServiceDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор услуги")
        self.setGeometry(200, 200, 400, 500)
        
        # Применяем стиль к окну
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        self.selected_service = None
        self._init_ui()
        self._load_services()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Выберите услугу:")
        title_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(title_label)
        
        # Список услуг
        self.services_list = QListWidget()
        self.services_list.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.services_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Выбрать")
        self.select_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setStyleSheet(BUTTON_STYLE)
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.select_btn.clicked.connect(self._select_service)
        self.cancel_btn.clicked.connect(self.reject)
        
    def _load_services(self):
        try:
            services = get_services()
            for service in services:
                self.services_list.addItem(f"{service['name']} - {service['cost']} руб.")
        except Exception as e:
            logger.error(f"Error loading services: {str(e)}")
            
    def _select_service(self):
        current_item = self.services_list.currentItem()
        if current_item:
            self.selected_service = current_item.text()
            self.accept() 
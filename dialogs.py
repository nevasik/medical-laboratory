from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from styles import *

class ErrorDialog(QDialog):
    """Диалог для отображения ошибок"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(300, 300, 400, 200)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self._init_ui(title, message)
        
    def _init_ui(self, title, message):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(LABEL_STYLE)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Сообщение
        message_label = QLabel(message)
        message_label.setStyleSheet(ERROR_LABEL_STYLE)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Кнопка OK
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class WarningDialog(QDialog):
    """Диалог для отображения предупреждений"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(WARNING_DIALOG_STYLE)
        
        layout = QVBoxLayout()
        
        # Сообщение
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Кнопка OK
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
        self.setFixedSize(400, 150)


class SuccessDialog(QDialog):
    """Диалог для отображения успешного выполнения операции"""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(300, 300, 400, 200)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self._init_ui(title, message)
        
    def _init_ui(self, title, message):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(LABEL_STYLE)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Сообщение
        message_label = QLabel(message)
        message_label.setStyleSheet(SUCCESS_LABEL_STYLE)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Кнопка OK
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
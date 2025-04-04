from config import Config
from ui.history_window import HistoryWindow
from PyQt6.QtCore import QTimer, QDateTime, Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QPushButton, QHBoxLayout, QMessageBox
)


class MainWindow(QMainWindow):
    def __init__(self, user_data, login_window):
        super().__init__()
        self.user_data = user_data
        self.login_window = login_window
        self.remaining_time = Config.SESSION_TIMEOUT_MIN if self._is_lab_technician() else None
        self.timer = None

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle(f"{self.user_data[0]} - {self.user_data[1] or 'Администратор'}")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        
        # Фото пользователя
        self.photo_label = QLabel()
        self._update_user_photo()
        self.layout.addWidget(self.photo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Информация о пользователе
        self._setup_user_info()
        
        # Таймер только для лаборантов
        if self._is_lab_technician():
            self._setup_session_timer()

        # Кнопки действий
        self._setup_action_buttons()

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def _setup_user_info(self):
        info_font = QFont("Arial", 14)
        self.name_label = QLabel(f"ФИО: {self.user_data[1] or 'Администратор'}")
        self.name_label.setFont(info_font)
        self.layout.addWidget(self.name_label)

        self.role_label = QLabel(f"Роль: {self.user_data[0]}")
        self.role_label.setFont(info_font)
        self.layout.addWidget(self.role_label)

    def _setup_session_timer(self):
        self.timer_label = QLabel(f"Осталось времени: {self.remaining_time} мин")
        self.layout.addWidget(self.timer_label)
        self.timer = QTimer()
        self.timer.setInterval(60000)  # 1 минута

    def _setup_action_buttons(self):
        button_layout = QHBoxLayout()

        logout_btn = QPushButton("Выйти")
        logout_btn.setFixedWidth(150)
        button_layout.addWidget(logout_btn)

        if self._is_admin():
            history_btn = QPushButton("История входов")
            history_btn.setFixedWidth(150)
            button_layout.addWidget(history_btn)

        self.layout.addLayout(button_layout)

    def _connect_signals(self):
        if self.timer:
            self.timer.timeout.connect(self._update_session_timer)
            self.timer.start()
        
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Выйти":
                btn.clicked.connect(self._logout)
            elif btn.text() == "История входов":
                btn.clicked.connect(self._open_history)

    def _update_user_photo(self):
        try:
            pixmap = QPixmap(self.user_data[2] or "default.png")
            if pixmap.isNull():
                raise FileNotFoundError
            self.photo_label.setPixmap(
                pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            )
        except (FileNotFoundError, TypeError):
            default_pixmap = QPixmap("default.png")
            self.photo_label.setPixmap(default_pixmap.scaled(150, 150))

    def _update_session_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Осталось времени: {self.remaining_time} мин")
        
        if self.remaining_time == 5:
            QMessageBox.warning(self, "Предупреждение", 
                              "До конца сеанса осталось 5 минут!")
        
        if self.remaining_time <= 0:
            self.timer.stop()
            self._logout(block=True)

    def _logout(self, block=False):
        if block and self._is_lab_technician():
            block_time = QDateTime.currentDateTime().addSecs(60)
            self.login_window.blocked_users[self.user_data[3]] = block_time
            QMessageBox.warning(self, "Блокировка", 
                              "Сеанс завершен! Повторный вход заблокирован на 1 минуту.")
        
        self.close()
        self.login_window.show()

    def _open_history(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

    def _is_admin(self):
        return self.user_data[0] == "Администратор"

    def _is_lab_technician(self):
        return self.user_data[0] in ['Лаборант', 'Лаборант-исследователь']

    def closeEvent(self, event):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        super().closeEvent(event)
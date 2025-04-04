from ui.main_window import MainWindow
from auth.service import AuthService
from auth.captcha import CaptchaGenerator
from config import Config
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox
)
from styles import COMMON_STYLE, LOGIN_EXTRA_STYLE


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 450)
        self.blocked_users = {}
        self.failed_attempts = 0
        self.captcha_generator = CaptchaGenerator()
        self.auth_service = AuthService()

        self._init_ui()
        self._connect_signals()

        self.setWindowIcon(QIcon('resources/logo.ico'))

    def _init_ui(self):
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap('resources/logo.png').scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        self.layout.insertWidget(0, logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.login_input = QLineEdit(placeholderText="Логин")
        self.password_input = QLineEdit(placeholderText="Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.captcha_label = QLabel()
        self.captcha_input = QLineEdit(placeholderText="Введите CAPTCHA")
        self.refresh_btn = QPushButton("Обновить CAPTCHA")
        self.toggle_captcha(False)

        self.show_password = QCheckBox("Показать пароль")
        self.login_button = QPushButton("Войти")

        widgets = [
            self.login_input, self.password_input,
            self.captcha_label, self.captcha_input, self.refresh_btn,
            self.show_password, self.login_button
        ]
        for widget in widgets:
            self.layout.addWidget(widget)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.setStyleSheet(COMMON_STYLE + LOGIN_EXTRA_STYLE)
        self.captcha_label.setObjectName("captcha_label")

    def _connect_signals(self):
        self.show_password.stateChanged.connect(self._toggle_password_visibility)
        self.login_button.clicked.connect(self._authenticate)
        self.refresh_btn.clicked.connect(self._generate_captcha)

    def toggle_captcha(self, show=True):
        self.captcha_label.setVisible(show)
        self.captcha_input.setVisible(show)
        self.refresh_btn.setVisible(show)
        if show:
            self._generate_captcha()

    def _generate_captcha(self):
        captcha_bytes = self.captcha_generator.generate()
        pixmap = QPixmap.fromImage(QImage.fromData(captcha_bytes))
        self.captcha_label.setPixmap(pixmap)
        self.captcha_input.clear()

    def _authenticate(self):
        login = self.login_input.text()
        password = self.password_input.text()
        captcha_entered = self.captcha_input.text()

        current_time = QDateTime.currentDateTime()
        if self._is_user_blocked(login, current_time):
            return

        if self.failed_attempts > 0 and not self._validate_captcha(captcha_entered):
            self._handle_failed_attempt(login, current_time)
            return

        user = self.auth_service.check_credentials(login, password)
        if user:
            self._handle_successful_login(login, user)
        else:
            self._handle_failed_login(login)

    def _is_user_blocked(self, login, current_time):
        if login in self.blocked_users and current_time < self.blocked_users[login]:
            remaining_sec = current_time.secsTo(self.blocked_users[login])
            QMessageBox.warning(self, "Блокировка", 
                f"Повторная попытка через {remaining_sec} сек")
            return True
        return False

    def _validate_captcha(self, captcha_entered):
        if not self.captcha_generator.verify(captcha_entered):
            QMessageBox.warning(self, "Ошибка", "Неверная CAPTCHA")
            self.failed_attempts += 1
            return False
        return True

    def _handle_successful_login(self, login, user):
        self.failed_attempts = 0
        self.toggle_captcha(False)
        self.auth_service.log_login_attempt(login, True, user[0])
        self._open_main_window(user)

    def _handle_failed_attempt(self, login, current_time):
        self.failed_attempts += 1
        self.blocked_users[login] = current_time.addSecs(Config.BLOCK_TIME_SEC)
        self.auth_service.log_login_attempt(login, False, 'unknown')
        self._generate_captcha()

    def _handle_failed_login(self, login):
        self.failed_attempts += 1
        if self.failed_attempts >= 1:
            self.toggle_captcha(True)
        QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        self.auth_service.log_login_attempt(login, False, 'unknown')

    def _toggle_password_visibility(self):
        show = self.show_password.isChecked()
        mode = QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(mode)

    def _open_main_window(self, user):
        self.hide()
        self.main_window = MainWindow(user, self)
        self.main_window.show()

    def closeEvent(self, event):
        self.auth_service = None
        super().closeEvent(event)
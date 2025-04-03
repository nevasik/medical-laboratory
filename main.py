import sys
import mysql.connector
import random
import string
from io import BytesIO
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import QTimer, QDateTime
from PIL import Image, ImageDraw, ImageFont

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 450)
        self.blocked_until = QDateTime()
        self.captcha_text = ""
        self.failed_attempts = 0
        self.blocked_users = {}  # Для блокировки по IP/логину

        # Основной контейнер
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Логин
        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Логин")
        self.layout.addWidget(self.login_input)

        # Пароль
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        # CAPTCHA элементы
        self.captcha_label = QLabel()
        self.captcha_input = QLineEdit()
        self.captcha_input.setPlaceholderText("Введите CAPTCHA")
        self.refresh_btn = QPushButton("Обновить CAPTCHA")
        self.layout.addWidget(self.captcha_label)
        self.layout.addWidget(self.captcha_input)
        self.layout.addWidget(self.refresh_btn)
        self.toggle_captcha(False)

        # Чекбокс и кнопка
        self.show_password = QCheckBox("Показать пароль")
        self.login_button = QPushButton("Войти")
        self.layout.addWidget(self.show_password)
        self.layout.addWidget(self.login_button)

        # Настройки
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Сигналы
        self.show_password.stateChanged.connect(self.toggle_password)
        self.login_button.clicked.connect(self.authenticate)
        self.refresh_btn.clicked.connect(self.generate_captcha)

    def toggle_captcha(self, show=True):
        """Показать/скрыть CAPTCHA элементы"""
        self.captcha_label.setVisible(show)
        self.captcha_input.setVisible(show)
        self.refresh_btn.setVisible(show)
        if show:
            self.generate_captcha()

    def generate_captcha(self):
        """Генерация CAPTCHA изображения"""
        self.captcha_text = ''.join(random.choices(
            string.ascii_letters + string.digits, 
            k=4
        )).upper()

        # Создаем изображение
        image = Image.new('RGB', (200, 100), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Рисуем искаженный текст
        font = ImageFont.load_default()
        for i, char in enumerate(self.captcha_text):
            x = 20 + i * 40 + random.randint(-15, 15)
            y = 30 + random.randint(-15, 15)
            draw.text(
                (x, y),
                char,
                fill=(random.randint(0, 150), 
                      random.randint(0, 150), 
                      random.randint(0, 150)),
                font=font
            )
        
        # Добавляем шум и линии
        for _ in range(100):
            draw.point(
                (random.randint(0, 200), random.randint(0, 100)),
                fill=(random.randint(0, 255), 
                      random.randint(0, 255), 
                      random.randint(0, 255))
            )
        
        for _ in range(5):
            draw.line(
                [(random.randint(0, 200), random.randint(0, 100)),
                 (random.randint(0, 200), random.randint(0, 100))],
                fill=(random.randint(0, 255), 
                      random.randint(0, 255), 
                      random.randint(0, 255)),
                width=2
            )

        # Конвертируем в QPixmap
        buffer = BytesIO()
        image.save(buffer, "PNG")
        pixmap = QPixmap.fromImage(QImage.fromData(buffer.getvalue()))
        self.captcha_label.setPixmap(pixmap)

    def authenticate(self):
        """Основная логика авторизации"""
        login = self.login_input.text()
        password = self.password_input.text()
        captcha_entered = self.captcha_input.text()

        # Проверка блокировки
        current_time = QDateTime.currentDateTime()
        if login in self.blocked_users:
            if current_time < self.blocked_users[login]:
                QMessageBox.warning(self, "Блокировка", 
                    f"Повторная попытка через {current_time.secsTo(self.blocked_users[login])} сек")
                return
            else:
                del self.blocked_users[login]

        # Проверка CAPTCHA
        if self.failed_attempts > 0:
            if captcha_entered.upper() != self.captcha_text.upper():
                self.failed_attempts += 1
                self.blocked_users[login] = current_time.addSecs(10)
                QMessageBox.warning(self, "Ошибка", "Неверная CAPTCHA")
                self.generate_captcha()
                return

        # Проверка учетных данных
        user = self.check_credentials(login, password)
        if user:
            self.failed_attempts = 0
            self.toggle_captcha(False)
            self.hide()
            self.main_window = MainWindow(user, self)
            self.main_window.show()
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 1:
                self.toggle_captcha(True)
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def check_credentials(self, login, password):
        """Проверка данных в БД"""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="59723833",
                database="medical_laboratory"
            )
            cursor = conn.cursor()

            # Администраторы
            cursor.execute("""
                SELECT 'Администратор', NULL, 'Администратор.png', login 
                FROM administrators 
                WHERE login = %s AND password = %s
            """, (login, password))
            admin = cursor.fetchone()

            # Лаборанты
            cursor.execute("""
                SELECT 
                    CASE WHEN is_researcher THEN 'Лаборант-исследователь' ELSE 'Лаборант' END,
                    full_name,
                    CASE WHEN is_researcher THEN 'laborant_2.png' ELSE 'laborant_1.jpeg' END,
                    login 
                FROM lab_technicians 
                WHERE login = %s AND password = %s
            """, (login, password))
            lab = cursor.fetchone()

            # Бухгалтеры
            cursor.execute("""
                SELECT 'Бухгалтер', full_name, 'Бухгалтер.jpeg', login 
                FROM accountants 
                WHERE login = %s AND password = %s
            """, (login, password))
            accountant = cursor.fetchone()

            return admin or lab or accountant

        except mysql.connector.Error as err:
            print(f"Ошибка БД: {err}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def toggle_password(self):
        """Показать/скрыть пароль"""
        if self.show_password.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

class MainWindow(QMainWindow):
    def __init__(self, user, login_window):
        super().__init__()
        self.user = user
        self.login_window = login_window
        self.setWindowTitle(f"{user[0]} - {user[1]}")
        self.setGeometry(100, 100, 800, 600)
        
        # Основной контейнер
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Фото
        self.photo_label = QLabel()
        self.update_photo()
        layout.addWidget(self.photo_label)
        
        # ФИО и роль
        info_font = QFont("Arial", 14)
        self.name_label = QLabel(f"ФИО: {user[1] if user[1] else 'Администратор'}")
        self.name_label.setFont(info_font)
        layout.addWidget(self.name_label)
        
        self.role_label = QLabel(f"Роль: {user[0]}")
        self.role_label.setFont(info_font)
        layout.addWidget(self.role_label)
        
        # Таймер для лаборантов
        if user[0] in ['Лаборант', 'Лаборант-исследователь']:
            self.remaining_time = 10
            self.timer_label = QLabel(f"Осталось времени: {self.remaining_time} мин")
            layout.addWidget(self.timer_label)
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(20000)  # 1 минута
            
        # Кнопка выхода
        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def update_photo(self):
        photo_path = self.user[2] if self.user[2] else "default.png"
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            pixmap.load("default.png")
            print(f"Файл {photo_path} не найден, используется default.png")
        self.photo_label.setPixmap(pixmap.scaled(150, 150))
        
    def update_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Осталось времени: {self.remaining_time} мин")
        
        if self.remaining_time == 5:
            QMessageBox.warning(self, "Предупреждение", "До конца сеанса осталось 5 минут!")
            
        if self.remaining_time <= 0:
            self.timer.stop()
            self.logout(True)
            
    def logout(self, block=False):
        self.close()
        if block:
            block_time = QDateTime.currentDateTime().addSecs(60)
            self.login_window.blocked_users[self.user[3]] = block_time
            QMessageBox.warning(self, "Блокировка", "Сеанс завершен! Повторный вход заблокирован на 1 минуту.")
            
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
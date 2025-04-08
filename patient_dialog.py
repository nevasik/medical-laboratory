from database.db import get_connection 
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QMessageBox, QHBoxLayout
)
from logger import logger
import hashlib
import re

class PatientDialog(QDialog):
    def __init__(self):
        try:
            super().__init__()
            logger.info("Initializing PatientDialog")
            self.setWindowTitle("Добавление пациента")
            self.setGeometry(100, 100, 400, 400)
            self._init_ui()
            self._connect_signals()
            logger.info("PatientDialog initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PatientDialog: {e}")
            raise

    def _init_ui(self):
        try:
            layout = QVBoxLayout()
            
            self.full_name = QLineEdit(placeholderText="ФИО")
            self.birthdate = QLineEdit(placeholderText="Дата рождения (ГГГГ-ММ-ДД)")
            self.passport_series = QLineEdit(placeholderText="Серия паспорта")
            self.passport_number = QLineEdit(placeholderText="Номер паспорта")
            self.phone = QLineEdit(placeholderText="Телефон")
            self.email = QLineEdit(placeholderText="Email")
            self.insurance_policy = QLineEdit(placeholderText="Номер полиса")
            self.insurance_type = QComboBox()
            self.insurance_type.addItems(["ОМС", "ДМС"])
            self.insurance_company = QComboBox()
            
            # Заполнение страховых компаний
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT company_id, name FROM insurance_companies")
                companies = cursor.fetchall()
                self.insurance_company.addItems([c[1] for c in companies])
                logger.debug(f"Loaded {len(companies)} insurance companies")
            
            layout.addWidget(QLabel("ФИО:"))
            layout.addWidget(self.full_name)
            layout.addWidget(QLabel("Дата рождения:"))
            layout.addWidget(self.birthdate)
            layout.addWidget(QLabel("Паспорт:"))
            layout.addWidget(self.passport_series)
            layout.addWidget(self.passport_number)
            layout.addWidget(QLabel("Контакты:"))
            layout.addWidget(self.phone)
            layout.addWidget(self.email)
            layout.addWidget(QLabel("Страховой полис:"))
            layout.addWidget(self.insurance_policy)
            layout.addWidget(self.insurance_type)
            layout.addWidget(self.insurance_company)
            
            btn_layout = QHBoxLayout()
            self.save_btn = QPushButton("Сохранить")
            self.cancel_btn = QPushButton("Отмена")
            btn_layout.addWidget(self.save_btn)
            btn_layout.addWidget(self.cancel_btn)
            layout.addLayout(btn_layout)
            
            self.setLayout(layout)
            logger.debug("UI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UI: {e}")
            raise

    def _connect_signals(self):
        try:
            self.save_btn.clicked.connect(self._save_patient)
            self.cancel_btn.clicked.connect(self.reject)
            logger.debug("Signals connected successfully")
        except Exception as e:
            logger.error(f"Error connecting signals: {e}")
            raise

    def _generate_login(self, full_name):
        # Преобразуем ФИО в латиницу
        translit = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        # Разбиваем ФИО на части
        parts = full_name.split()
        if len(parts) < 2:
            # Если только одно слово, берем первые 3 буквы
            name = parts[0]
            for cyr, lat in translit.items():
                name = name.replace(cyr, lat)
            base = name[:3].lower()
        else:
            # Преобразуем фамилию в латиницу
            surname = parts[0]
            for cyr, lat in translit.items():
                surname = surname.replace(cyr, lat)
            
            # Берем первые буквы имени и отчества
            initials = ''
            for part in parts[1:]:
                initial = part[0]
                for cyr, lat in translit.items():
                    initial = initial.replace(cyr, lat)
                initials += initial.upper()
            
            base = f"{surname.capitalize()}{initials}"
        
        # Добавляем случайное число для уникальности
        import random
        name = f"{base}{random.randint(10, 99)}"
        
        return name

    def _generate_password(self):
        # Генерируем случайный пароль из 8 символов
        import random
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(8))

    def _save_patient(self):
        try:
            data = {
                'full_name': self.full_name.text(),
                'birthdate': self.birthdate.text(),
                'passport_series': self.passport_series.text(),
                'passport_number': self.passport_number.text(),
                'phone': self.phone.text(),
                'email': self.email.text(),
                'insurance_policy': self.insurance_policy.text(),
                'insurance_type': self.insurance_type.currentText(),
                'insurance_company': self.insurance_company.currentText()
            }
            
            # Валидация
            if not all(data.values()):
                logger.warning("Not all fields are filled")
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return
            
            # Генерируем логин и пароль
            login = self._generate_login(data['full_name'])
            password = self._generate_password()
            
            # Хешируем пароль
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (
                        login, password, full_name, birthdate, passport_series, 
                        passport_number, phone, email, insurance_policy_number, 
                        insurance_policy_type, company_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                              (SELECT company_id FROM insurance_companies WHERE name=%s))
                """, (
                    login,
                    hashed_password,
                    data['full_name'],
                    data['birthdate'],
                    data['passport_series'],
                    data['passport_number'],
                    data['phone'],
                    data['email'],
                    data['insurance_policy'],
                    data['insurance_type'],
                    data['insurance_company']
                ))
                conn.commit()
                logger.info(f"Patient saved successfully: {data['full_name']}")
            
            # Сохраняем данные для возврата
            self.patient_data = data
            
            # Показываем сообщение с логином и паролем
            QMessageBox.information(self, "Успех", 
                f"Пациент успешно добавлен!\n\nЛогин: {login}\nПароль: {password}\n\n"
                "Сохраните эти данные для входа в систему.")
            
            self.accept()
        except Exception as e:
            logger.error(f"Error saving patient: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные пациента")
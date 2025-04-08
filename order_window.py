from PyQt6.QtCore import Qt, QDateTime
from database.connection import get_connection
from database.db import get_services, search_patients
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QListWidget, QListWidgetItem
)   
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from patient_dialog import PatientDialog
import barcode
from reportlab.lib.pagesizes import A4
import base64
import os
from logger import logger
from PIL import Image, ImageDraw, ImageFont
import random
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from styles import *  # Импортируем все стили
from dialogs import WarningDialog, SuccessDialog, ErrorDialog  # Импортируем диалоги


class ServiceDialog(QDialog):
    """Диалог для выбора услуги"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор услуги")
        self.setGeometry(200, 200, 400, 500)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        self.selected_service = None
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Выберите услугу:")
        title_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(title_label)
        
        # Список услуг
        self.services_list = QListWidget()
        self.services_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #76E383;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-family: "Comic Sans MS";
                font-size: 12pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #76E383;
            }
            QListWidget::item:selected {
                background-color: #497C51;
                color: white;
            }
        """)
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
        
        # Заполняем список услуг
        self._load_services()
        
        # Подключаем сигналы
        self.select_btn.clicked.connect(self._select_service)
        self.cancel_btn.clicked.connect(self.reject)
        self.services_list.itemDoubleClicked.connect(self._select_service)
        
    def _load_services(self):
        try:
            services, _ = get_services()
            for service in services:
                item = QListWidgetItem(f"{service[1]} - {service[2]} руб.")
                item.setData(Qt.ItemDataRole.UserRole, service)
                self.services_list.addItem(item)
        except Exception as e:
            logger.error(f"Error loading services: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить список услуг")
            
    def _select_service(self):
        current_item = self.services_list.currentItem()
        if current_item:
            self.selected_service = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите услугу из списка")


class OrderWindow(QDialog):
    def __init__(self):
        try:
            super().__init__()
            logger.info("Initializing OrderWindow")
            self.setWindowTitle("Формирование заказа")
            self.setGeometry(100, 100, 800, 600)
            
            # Применяем стиль к окну
            self.setStyleSheet(MAIN_WINDOW_STYLE)
            
            # Инициализируем переменные по умолчанию
            self.order_number = 1
            self.tube_code = None
            self.barcode_path = None
            
            # Инициализируем UI
            self._init_ui()
            
            # Генерируем номер заказа
            self._generate_order_number()
            
            # Подключаем сигналы
            self._connect_signals()
            
            logger.info("OrderWindow initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OrderWindow: {e}")
            QMessageBox.critical(self, "Ошибка инициализации", 
                               f"Произошла ошибка при инициализации окна: {str(e)}")
            super().__init__()
            self.setWindowTitle("Формирование заказа")
            self.setGeometry(100, 100, 800, 600)
            self.order_number = 1
            self.tube_code = None
            self.barcode_path = None

    def _init_ui(self):
        try:
            layout = QVBoxLayout()
            
            # Код пробирки
            code_label = QLabel("Код пробирки:")
            code_label.setStyleSheet(LABEL_STYLE)
            self.code_input = QLineEdit()
            self.code_input.setStyleSheet(INPUT_STYLE)
            self._update_tube_code_placeholder()  # Обновляем подсказку
            layout.addWidget(code_label)
            layout.addWidget(self.code_input)
            
            # Пациент
            patient_label = QLabel("Пациент:")
            patient_label.setStyleSheet(LABEL_STYLE)
            self.patient_search = QLineEdit()
            self.patient_search.setStyleSheet(INPUT_STYLE)
            self.patient_search.setPlaceholderText("Поиск пациента...")
            self.patient_list = QComboBox()
            self.patient_list.setStyleSheet(COMBOBOX_STYLE)
            layout.addWidget(patient_label)
            layout.addWidget(self.patient_search)
            layout.addWidget(self.patient_list)
            self.add_patient_btn = QPushButton("Добавить пациента")
            self.add_patient_btn.setStyleSheet(BUTTON_STYLE)
            layout.addWidget(self.add_patient_btn)
            
            # Услуги
            services_label = QLabel("Услуги:")
            services_label.setStyleSheet(LABEL_STYLE)
            layout.addWidget(services_label)
            self.services_table = QTableWidget()
            self.services_table.setStyleSheet(TABLE_STYLE)
            self.services_table.setColumnCount(2)
            self.services_table.setHorizontalHeaderLabels(["Услуга", "Стоимость"])
            layout.addWidget(self.services_table)
            self.add_service_btn = QPushButton("Добавить услугу")
            self.add_service_btn.setStyleSheet(BUTTON_STYLE)
            layout.addWidget(self.add_service_btn)
            
            # Кнопки управления
            btn_layout = QHBoxLayout()
            self.generate_btn = QPushButton("Сформировать заказ")
            self.generate_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
            self.cancel_btn = QPushButton("Отмена")
            self.cancel_btn.setStyleSheet(BUTTON_STYLE)
            btn_layout.addWidget(self.generate_btn)
            btn_layout.addWidget(self.cancel_btn)
            layout.addLayout(btn_layout)
            
            self.setLayout(layout)
            logger.debug("UI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UI: {e}")
            QMessageBox.critical(self, "Ошибка инициализации UI", 
                               f"Произошла ошибка при инициализации интерфейса: {str(e)}")
            # Создаем минимальный интерфейс
            layout = QVBoxLayout()
            
            # Инициализируем все необходимые переменные
            self.code_input = QLineEdit()
            self.patient_search = QLineEdit()
            self.patient_list = QComboBox()
            self.add_patient_btn = QPushButton("Добавить пациента")
            self.services_table = QTableWidget()
            self.add_service_btn = QPushButton("Добавить услугу")
            self.generate_btn = QPushButton("Сформировать заказ")
            self.cancel_btn = QPushButton("Отмена")
            
            # Добавляем минимальный интерфейс
            layout.addWidget(QLabel("Ошибка инициализации интерфейса"))
            layout.addWidget(self.cancel_btn)
            
            self.setLayout(layout)

    def _update_tube_code_placeholder(self):
        """Обновляет подсказку в поле ввода кода пробирки"""
        try:
            with get_connection() as conn:
                if not conn:
                    logger.error("Failed to connect to database")
                    self.code_input.setPlaceholderText("Введите или сканируйте код пробирки")
                    return

                cursor = conn.cursor()
                cursor.execute("SELECT MAX(CAST(tube_code AS UNSIGNED)) FROM orders WHERE tube_code REGEXP '^[0-9]+$'")
                result = cursor.fetchone()[0]
                
                if result is None:
                    next_code = "1"
                else:
                    next_code = str(int(result) + 1)
                
                self.code_input.setPlaceholderText(f"Следующий код пробирки: {next_code}")
                logger.debug(f"Updated tube code placeholder: {next_code}")
        except Exception as e:
            logger.error(f"Error updating tube code placeholder: {e}")
            self.code_input.setPlaceholderText("Введите или сканируйте код пробирки")

    def _generate_order_number(self):
        try:
            logger.debug("Attempting to connect to database to generate order number")
            with get_connection() as conn:
                if not conn:
                    logger.error("Failed to connect to database")
                    self.order_number = 1
                    return

                logger.debug("Successfully connected to database")
                cursor = conn.cursor()
                logger.debug("Executing query to get max order_id")
                cursor.execute("SELECT MAX(order_id) FROM orders")
                max_id = cursor.fetchone()[0] or 0
                self.order_number = max_id + 1
                logger.debug(f"Generated order number: {self.order_number}")
        except Exception as e:
            logger.error(f"Error generating order number: {e}")
            self.order_number = 1

    def _connect_signals(self):
        try:
            # Проверяем, что все необходимые переменные инициализированы
            if not hasattr(self, 'code_input') or not hasattr(self, 'patient_search') or \
               not hasattr(self, 'patient_list') or not hasattr(self, 'add_patient_btn') or \
               not hasattr(self, 'services_table') or not hasattr(self, 'add_service_btn') or \
               not hasattr(self, 'generate_btn') or not hasattr(self, 'cancel_btn'):
                logger.error("Some UI elements are not initialized")
                return
                
            self.code_input.textChanged.connect(self._process_code)
            self.patient_search.textChanged.connect(self._search_patient)
            self.add_patient_btn.clicked.connect(self._open_patient_dialog)
            self.add_service_btn.clicked.connect(self._add_service)
            self.generate_btn.clicked.connect(self._generate_order)
            self.cancel_btn.clicked.connect(self.reject)
            logger.debug("Signals connected successfully")
        except Exception as e:
            logger.error(f"Error connecting signals: {e}")
            QMessageBox.critical(self, "Ошибка подключения сигналов", 
                               f"Произошла ошибка при подключении сигналов: {str(e)}")

    def _process_code(self):
        try:
            code = self.code_input.text().strip()
            if not code:  # If code is empty, clear tube_code and return
                self.tube_code = None
                return
                
            if code.endswith('\r'):
                code = code[:-1]
                
            with get_connection() as conn:
                if not conn:
                    logger.error("Failed to connect to database")
                    warning_dialog = WarningDialog("Предупреждение", 
                        "Не удалось подключиться к базе данных.\nКод будет принят без проверки.")
                    warning_dialog.exec()
                    self.tube_code = code
                    return

                cursor = conn.cursor()
                cursor.execute("SELECT order_id FROM orders WHERE tube_code = %s AND is_archived = 0", (code,))
                if cursor.fetchone():
                    logger.warning(f"Duplicate tube code: {code}")
                    warning_dialog = WarningDialog("Ошибка", 
                        f"Код пробирки {code} уже существует!\nПожалуйста, введите другой код.")
                    warning_dialog.exec()
                    self.code_input.clear()
                    self.tube_code = None
                    return
                self.tube_code = code
                logger.debug(f"Processed tube code: {code}")
        except Exception as e:
            logger.error(f"Error processing code: {e}")
            warning_dialog = WarningDialog("Предупреждение", 
                "Не удалось проверить код.\nКод будет принят без проверки.")
            warning_dialog.exec()
            self.tube_code = code

    def _search_patient(self):
        try:
            term = self.patient_search.text().strip()
            if not term:
                self.patient_list.clear()
                return
            
            patients = search_patients(term)
            self.patient_list.clear()
            for p in patients:
                # p[0] - id, p[1] - ФИО, p[2] - дата рождения, p[3] - номер полиса
                self.patient_list.addItem(f"{p[1]}", userData={'id': p[0], 'birth_date': p[2], 'insurance': p[3]})
            logger.debug(f"Found {len(patients)} patients for search term: {term}")
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось выполнить поиск пациентов")

    def _open_patient_dialog(self):
        try:
            dialog = PatientDialog()
            if dialog.exec():
                self.patient_search.setText(dialog.patient_data['full_name'])
                logger.debug(f"Added new patient: {dialog.patient_data['full_name']}")
        except Exception as e:
            logger.error(f"Error opening patient dialog: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть диалог добавления пациента")

    def _add_service(self):
        try:
            dialog = ServiceDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_service:
                selected = dialog.selected_service
                row = self.services_table.rowCount()
                self.services_table.insertRow(row)
                
                # Создаем и стилизуем ячейки
                name_item = QTableWidgetItem(selected[1])
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                name_item.setForeground(Qt.GlobalColor.black)  # Устанавливаем черный цвет текста
                
                cost_item = QTableWidgetItem(str(selected[2]))
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                cost_item.setForeground(Qt.GlobalColor.black)  # Устанавливаем черный цвет текста
                
                self.services_table.setItem(row, 0, name_item)
                self.services_table.setItem(row, 1, cost_item)
                
                # Устанавливаем ширину столбцов
                self.services_table.setColumnWidth(0, 300)
                self.services_table.setColumnWidth(1, 100)
                
                logger.debug(f"Added service: {selected[1]}")
        except Exception as e:
            logger.error(f"Error adding service: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить услугу")

    def _clear_form(self):
        """Очищает все поля формы после успешного создания заказа"""
        try:
            # Очищаем поле кода пробирки
            self.code_input.clear()
            
            # Обновляем подсказку кода пробирки
            self._update_tube_code_placeholder()
            
            # Очищаем поле поиска пациента
            self.patient_search.clear()
            
            # Очищаем выпадающий список пациентов
            self.patient_list.clear()
            
            # Очищаем таблицу услуг
            self.services_table.setRowCount(0)
            
            # Генерируем новый номер заказа
            self._generate_order_number()
            
            logger.debug("Form cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing form: {e}")
            QMessageBox.warning(self, "Предупреждение", 
                              "Не удалось очистить форму.\nПожалуйста, очистите поля вручную.")

    def _generate_order(self):
        try:
            # Проверяем, заполнен ли код пробирки
            if not self.tube_code:
                logger.warning("Tube code is not filled")
                warning_dialog = WarningDialog("Ошибка", "Введите код пробирки!", self)
                warning_dialog.exec()
                return
                
            # Получаем ID пациента из userData
            patient_data = self.patient_list.currentData()
            if not patient_data or 'id' not in patient_data:
                logger.warning("No patient selected")
                warning_dialog = WarningDialog("Ошибка", "Выберите пациента!", self)
                warning_dialog.exec()
                return
            
            patient_id = patient_data['id']  # Получаем именно ID пациента
            
            if self.services_table.rowCount() == 0:
                logger.warning("No services added")
                warning_dialog = WarningDialog("Ошибка", "Добавьте хотя бы одну услугу!", self)
                warning_dialog.exec()
                return

            raw_code = self.code_input.text().strip()
            code = raw_code[:-1] if raw_code.endswith('\r') else raw_code
            
            # Проверяем существование кода в базе данных
            with get_connection() as conn:
                if not conn:
                    logger.error("Failed to connect to database to check code")
                    warning_dialog = WarningDialog("Предупреждение", 
                                                  "Не удалось проверить уникальность кода.\nПродолжаем без проверки.", self)
                    warning_dialog.exec()
                else:
                    cursor = conn.cursor()
                    cursor.execute("SELECT order_id FROM orders WHERE tube_code = %s AND is_archived = 0", (code,))
                    if cursor.fetchone():
                        logger.warning(f"Duplicate tube code: {code}")
                        error_dialog = ErrorDialog("Ошибка", "Код уже существует!", self)
                        error_dialog.exec()
                        return
            
            # Создаем директорию для штрих-кодов, если она не существует
            if not os.path.exists('barcodes'):
                os.makedirs('barcodes')
                
            try:
                self._generate_barcode(code)
                pdf_path = self._generate_pdf()
            except Exception as e:
                logger.error(f"Error generating files: {e}")
                QMessageBox.critical(self, "Ошибка", 
                                   "Не удалось сгенерировать файлы заказа")
                return
            
            # Рассчитываем общую стоимость заказа
            total = 0
            for r in range(self.services_table.rowCount()):
                cost_item = self.services_table.item(r, 1)
                if cost_item:
                    try:
                        cost = float(cost_item.text().replace(',', '.'))
                        total += cost
                    except ValueError:
                        logger.warning(f"Invalid cost value in row {r}: {cost_item.text()}")
            
            # Сохраняем заказ в базе данных
            with get_connection() as conn:
                if not conn:
                    logger.error("Failed to connect to database to save order")
                    QMessageBox.critical(self, "Ошибка", 
                                       "Не удалось подключиться к базе данных.\nЗаказ не может быть сохранен.")
                    return

                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO orders (patient_id, creation_date, tube_code, status, total)
                        VALUES (%s, NOW(), %s, 'pending', %s)
                    """, (patient_id, code, total))
                    order_id = cursor.lastrowid
                    
                    for r in range(self.services_table.rowCount()):
                        service = self.services_table.item(r, 0).text()
                        cursor.execute("""
                            INSERT INTO order_services (order_id, service_id, status)
                            VALUES (%s, (SELECT service_id FROM services WHERE name=%s), 'pending')
                        """, (order_id, service))
                    
                    conn.commit()
                    logger.info(f"Order {order_id} created successfully with total cost: {total}")
                    
                    # Показываем диалог успеха
                    success_message = f"Заказ {order_id} сформирован!\nОбщая стоимость: {total:.2f} руб.\nPDF: {pdf_path}"
                    success_dialog = SuccessDialog("Успех", success_message, self)
                    success_dialog.exec()
                    
                    # Очищаем форму после успешного создания заказа
                    self._clear_form()
                    
                except Exception as e:
                    logger.error(f"Error saving order to database: {e}")
                    QMessageBox.critical(self, "Ошибка", 
                                       "Произошла ошибка при сохранении заказа в базе данных")
                    return
        except Exception as e:
            logger.error(f"Error generating order: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось сформировать заказ")

    def _generate_barcode(self, code):
        try:
            # Создаем директорию для штрих-кодов, если она не существует
            if not os.path.exists('barcodes'):
                os.makedirs('barcodes')
                
            # Получаем текущую дату в формате YYYYMMDD
            current_date = QDateTime.currentDateTime().toString("yyyyMMdd")
            
            # Генерируем уникальный код из 6 символов
            unique_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Формируем полный код для штрих-кода
            full_code = f"{code}{current_date}{unique_code}"
            
            # Создаем изображение штрих-кода
            from PIL import Image, ImageDraw, ImageFont
            
            # Параметры штрих-кода (в мм)
            bar_width_unit = 0.15  # мм на единицу
            zero_width = 1.35  # мм для нуля
            spacing = 0.2  # мм между штрихами
            symbol_height = 25.93  # мм высота символа
            bar_height = 22.85  # мм высота штриха
            left_margin = 3.63  # мм свободная зона слева
            right_margin = 2.31  # мм свободная зона справа
            guard_bar_extension = 1.65  # мм удлинение ограничивающих знаков
            digit_height = 2.75  # мм высота цифр
            digit_to_bar_gap = 0.165  # мм расстояние от цифр до штрихов
            digit_spacing = 0.5  # мм дополнительное расстояние между цифрами
            
            # Масштаб для преобразования мм в пиксели (300 DPI = 11.8 пикселей на мм)
            scale = 11.8
            
            # Рассчитываем ширину изображения
            total_width = left_margin + right_margin  # Начальная ширина с учетом отступов
            
            # Добавляем ширину для каждой цифры
            for digit in full_code:
                if digit == '0':
                    total_width += zero_width
                else:
                    total_width += int(digit) * bar_width_unit
                total_width += spacing
            
            # Создаем изображение
            width_px = int(total_width * scale)
            height_px = int(symbol_height * scale)
            image = Image.new('RGB', (width_px, height_px), 'white')
            draw = ImageDraw.Draw(image)
            
            # Рисуем штрихи
            x_pos = int(left_margin * scale)  # Начинаем с левого отступа
            
            # Рисуем левый ограничивающий знак (удлиненный)
            draw.rectangle([x_pos, 0, x_pos + int(bar_width_unit * scale), 
                           int((bar_height + guard_bar_extension) * scale)], fill='black')
            x_pos += int(bar_width_unit * scale) + int(spacing * scale)
            
            # Рисуем штрихи
            for i, digit in enumerate(full_code):
                # Рисуем штрих
                if digit == '0':
                    # Для нуля оставляем белый штрих
                    x_pos += int(zero_width * scale)
                else:
                    # Для остальных цифр рисуем черную полоску
                    bar_width_px = int(int(digit) * bar_width_unit * scale)
                    
                    # Определяем, является ли это центральным или ограничивающим знаком
                    is_guard_bar = (i == 0 or i == len(full_code) - 1 or 
                                   (i == len(full_code) // 2 - 1 and len(full_code) % 2 == 0))
                    
                    if is_guard_bar:
                        # Удлиняем ограничивающие знаки
                        draw.rectangle([x_pos, 0, x_pos + bar_width_px, 
                                       int((bar_height + guard_bar_extension) * scale)], fill='black')
                    else:
                        # Обычный штрих
                        draw.rectangle([x_pos, 0, x_pos + bar_width_px, 
                                       int(bar_height * scale)], fill='black')
                    
                    x_pos += bar_width_px
                
                # Добавляем расстояние между штрихами
                x_pos += int(spacing * scale)
            
            # Рисуем правый ограничивающий знак (удлиненный)
            draw.rectangle([x_pos, 0, x_pos + int(bar_width_unit * scale), 
                           int((bar_height + guard_bar_extension) * scale)], fill='black')
            
            # Теперь рисуем цифры отдельно, чтобы они не слипались
            x_pos = int(left_margin * scale)  # Сбрасываем позицию
            
            # Пытаемся загрузить шрифт
            try:
                font = ImageFont.truetype("arial.ttf", int(digit_height * scale))
            except:
                font = ImageFont.load_default()
            
            # Рисуем цифры над штрихами с правильным позиционированием
            for i, digit in enumerate(full_code):
                # Позиция для текста
                if digit == '0':
                    # Для нуля используем фиксированную ширину
                    digit_width = int(zero_width * scale)
                else:
                    # Для остальных цифр ширина зависит от значения
                    digit_width = int(int(digit) * bar_width_unit * scale)
                
                # Центрируем цифру над штрихом
                text_x = x_pos + (digit_width // 2) - (int(digit_height * scale) // 2)
                text_y = int((symbol_height - digit_height - digit_to_bar_gap) * scale)
                
                # Рисуем текст
                draw.text((text_x, text_y), digit, fill='black', font=font)
                
                # Перемещаемся к следующей цифре
                if digit == '0':
                    x_pos += int(zero_width * scale)
                else:
                    x_pos += int(int(digit) * bar_width_unit * scale)
                
                # Добавляем расстояние между штрихами и дополнительное расстояние между цифрами
                x_pos += int(spacing * scale) + int(digit_spacing * scale)
            
            # Сохраняем изображение
            filename = f"barcodes/barcode_{code}.png"
            image.save(filename)
            self.barcode_path = filename
            logger.debug(f"Generated custom barcode: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating barcode: {e}")
            QMessageBox.critical(self, "Ошибка", 
                               "Не удалось сгенерировать штрих-код")
            raise

    def _generate_pdf(self):
        try:
            # Создаем директорию для PDF, если она не существует
            if not os.path.exists('pdfs'):
                os.makedirs('pdfs')
                
            # Получаем информацию о пациенте
            patient_data = self.patient_list.currentData()
            patient_name = self.patient_list.currentText()
            
            # Получаем информацию о заказе
            order_number = self.order_number
            tube_code = self.code_input.text().strip()
            
            # Получаем текущую дату
            current_date = QDateTime.currentDateTime().toString("dd.MM.yyyy")
            
            # Получаем информацию об услугах
            services = []
            total_cost = 0
            for r in range(self.services_table.rowCount()):
                service_name = self.services_table.item(r, 0).text()
                service_cost = self.services_table.item(r, 1).text()
                services.append((service_name, service_cost))
                try:
                    total_cost += float(service_cost.replace(',', '.'))
                except ValueError:
                    logger.warning(f"Invalid cost value: {service_cost}")
            
            # Создаем PDF-файл
            pdf_path = f"pdfs/order_{order_number}.pdf"
            
            # Регистрируем шрифты для поддержки кириллицы
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
                pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
                font_name = 'Arial'
                font_name_bold = 'Arial-Bold'
            except:
                # Если Arial недоступен, используем DejaVuSans
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
                    font_name = 'DejaVuSans'
                    font_name_bold = 'DejaVuSans-Bold'
                except:
                    # Если и DejaVuSans недоступен, используем стандартный шрифт
                    font_name = 'Helvetica'
                    font_name_bold = 'Helvetica-Bold'
                    logger.warning("Using fallback font Helvetica - cyrillic characters may not display correctly")
            
            c = canvas.Canvas(pdf_path, pagesize=A4)
            
            # Добавляем заголовок
            c.setFont(font_name_bold, 16)
            c.drawString(50, 800, "ЗАКАЗ НА ЛАБОРАТОРНОЕ ИССЛЕДОВАНИЕ")
            
            # Добавляем информацию о заказе
            c.setFont(font_name, 12)
            c.drawString(50, 750, f"Дата заказа: {current_date}")
            c.drawString(50, 730, f"Номер заказа: {order_number}")
            c.drawString(50, 710, f"Код пробирки: {tube_code}")
            
            # Добавляем информацию о пациенте
            c.drawString(50, 680, f"ФИО пациента: {patient_name}")
            c.drawString(50, 660, f"Дата рождения: {patient_data['birth_date']}")
            c.drawString(50, 640, f"Номер страхового полиса: {patient_data['insurance']}")
            
            # Добавляем таблицу услуг
            c.drawString(50, 550, "Перечень услуг:")
            
            # Заголовки таблицы
            c.setFont(font_name_bold, 10)
            c.drawString(50, 530, "№")
            c.drawString(80, 530, "Наименование услуги")
            c.drawString(400, 530, "Стоимость (руб.)")
            
            # Данные таблицы
            c.setFont(font_name, 10)
            y = 510
            for i, (service_name, service_cost) in enumerate(services, 1):
                c.drawString(50, y, str(i))
                c.drawString(80, y, service_name)
                c.drawString(400, y, service_cost)
                y -= 20
            
            # Итоговая стоимость
            c.setFont(font_name_bold, 12)
            c.drawString(350, y - 20, f"Итого: {total_cost:.2f} руб.")
            
            # Добавляем штрих-код сразу под таблицей услуг
            if self.barcode_path and os.path.exists(self.barcode_path):
                c.drawImage(self.barcode_path, 50, y - 90, width=200, height=50)
            
            # Сохраняем PDF
            c.save()
            logger.debug(f"Generated PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            QMessageBox.critical(self, "Ошибка", 
                               "Не удалось сгенерировать PDF")
            raise
import pymysql
import pymysql.cursors
import random
from datetime import datetime, timedelta

SQL_CREATE_DB = """
CREATE DATABASE IF NOT EXISTS session4 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
"""

SQL_USE_DB = """
USE my_apteka_db;
"""

SQL_CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS supplier (
        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
        legal_name VARCHAR(255) NOT NULL,
        legal_address VARCHAR(255) NOT NULL,
        inn VARCHAR(20),
        contract_number VARCHAR(50),
        okpo_code VARCHAR(20),
        phone VARCHAR(20),
        contact_person VARCHAR(255)
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS warehouse (
        warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
        warehouse_name VARCHAR(100) NOT NULL,
        warehouse_addr VARCHAR(255) NOT NULL,
        description TEXT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS category (
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(100) NOT NULL,
        description TEXT,
        is_consumable BOOLEAN NOT NULL DEFAULT FALSE,
        min_stock INT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS cabinet (
        cabinet_id INT AUTO_INCREMENT PRIMARY KEY,
        cabinet_name VARCHAR(50) NOT NULL,
        description TEXT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS employee (
        employee_id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        address VARCHAR(255),
        phone VARCHAR(20),
        email VARCHAR(100),
        position VARCHAR(50)
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS equipment (
        equipment_id INT AUTO_INCREMENT PRIMARY KEY,
        equipment_name VARCHAR(255) NOT NULL,
        category_id INT NOT NULL,
        warehouse_id INT NULL,
        cabinet_id INT NULL,
        employee_id INT NULL,
        shelf_location VARCHAR(50),
        max_shelf_life INT,
        current_stock INT NOT NULL DEFAULT 0,
        min_stock INT,
        CONSTRAINT fk_equipment_category
          FOREIGN KEY (category_id)
          REFERENCES category(category_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT,
        CONSTRAINT fk_equipment_warehouse
          FOREIGN KEY (warehouse_id)
          REFERENCES warehouse(warehouse_id)
          ON UPDATE CASCADE
          ON DELETE SET NULL,
        CONSTRAINT fk_equipment_cabinet
          FOREIGN KEY (cabinet_id)
          REFERENCES cabinet(cabinet_id)
          ON UPDATE CASCADE
          ON DELETE SET NULL,
        CONSTRAINT fk_equipment_employee
          FOREIGN KEY (employee_id)
          REFERENCES employee(employee_id)
          ON UPDATE CASCADE
          ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS medicine (
        medicine_id INT AUTO_INCREMENT PRIMARY KEY,
        medicine_name VARCHAR(255) NOT NULL,
        description TEXT,
        medicine_form VARCHAR(50),
        is_rx_required BOOLEAN NOT NULL DEFAULT FALSE
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS medicine_batch (
        batch_id INT AUTO_INCREMENT PRIMARY KEY,
        medicine_id INT NOT NULL,
        supplier_id INT NOT NULL,
        warehouse_id INT NOT NULL,
        batch_number VARCHAR(50),
        quantity_in_stock INT NOT NULL DEFAULT 0,
        price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        social_discount DECIMAL(5,2),
        manufacture_date DATE,
        expiry_date DATE,
        CONSTRAINT fk_mbatch_medicine
          FOREIGN KEY (medicine_id)
          REFERENCES medicine(medicine_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT,
        CONSTRAINT fk_mbatch_supplier
          FOREIGN KEY (supplier_id)
          REFERENCES supplier(supplier_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT,
        CONSTRAINT fk_mbatch_warehouse
          FOREIGN KEY (warehouse_id)
          REFERENCES warehouse(warehouse_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS supply_order (
        supply_order_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_id INT NOT NULL,
        order_date DATE NOT NULL,
        shipment_date DATE,
        status VARCHAR(50),
        comments TEXT,
        CONSTRAINT fk_supply_order_supplier
          FOREIGN KEY (supplier_id)
          REFERENCES supplier(supplier_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS supply_order_item (
        supply_order_id INT NOT NULL,
        batch_id INT NOT NULL,
        ordered_qty INT NOT NULL,
        delivered_qty INT,
        price_at_order DECIMAL(10,2),
        PRIMARY KEY (supply_order_id, batch_id),
        CONSTRAINT fk_soi_supply_order
          FOREIGN KEY (supply_order_id)
          REFERENCES supply_order(supply_order_id)
          ON UPDATE CASCADE
          ON DELETE CASCADE,
        CONSTRAINT fk_soi_batch
          FOREIGN KEY (batch_id)
          REFERENCES medicine_batch(batch_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS client (
        client_id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        email VARCHAR(100),
        discount_rate DECIMAL(5,2) DEFAULT 0.00
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS purchase (
        purchase_id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        purchase_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        CONSTRAINT fk_purchase_client
          FOREIGN KEY (client_id)
          REFERENCES client(client_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS purchase_item (
        purchase_id INT NOT NULL,
        batch_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (purchase_id, batch_id),
        CONSTRAINT fk_pi_purchase
          FOREIGN KEY (purchase_id)
          REFERENCES purchase(purchase_id)
          ON UPDATE CASCADE
          ON DELETE CASCADE,
        CONSTRAINT fk_pi_batch
          FOREIGN KEY (batch_id)
          REFERENCES medicine_batch(batch_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS contract (
        contract_id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT NOT NULL,
        service_type VARCHAR(50),
        contract_date DATE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        status VARCHAR(50),
        CONSTRAINT fk_contract_client
          FOREIGN KEY (client_id)
          REFERENCES client(client_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS invoice (
        invoice_id INT AUTO_INCREMENT PRIMARY KEY,
        contract_id INT NOT NULL,
        invoice_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        is_paid BOOLEAN NOT NULL DEFAULT FALSE,
        payment_date DATE,
        CONSTRAINT fk_invoice_contract
          FOREIGN KEY (contract_id)
          REFERENCES contract(contract_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS appointment (
        appointment_id INT AUTO_INCREMENT PRIMARY KEY,
        contract_id INT,
        employee_id INT NOT NULL,
        appointment_dt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        cabinet_id INT,
        notes TEXT,
        CONSTRAINT fk_appointment_contract
          FOREIGN KEY (contract_id)
          REFERENCES contract(contract_id)
          ON UPDATE CASCADE
          ON DELETE SET NULL,
        CONSTRAINT fk_appointment_employee
          FOREIGN KEY (employee_id)
          REFERENCES employee(employee_id)
          ON UPDATE CASCADE
          ON DELETE RESTRICT,
        CONSTRAINT fk_appointment_cabinet
          FOREIGN KEY (cabinet_id)
          REFERENCES cabinet(cabinet_id)
          ON UPDATE CASCADE
          ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """,

    # Дополнительно, если нужно именно patient (отдельно от client),
    """
    CREATE TABLE IF NOT EXISTS patient (
        patient_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20),
        dob DATE
    ) ENGINE=InnoDB;
    """,

    """
    CREATE TABLE IF NOT EXISTS quality_control (
                                               control_id INT AUTO_INCREMENT PRIMARY KEY,
                                               appointment_id INT NOT NULL,
                                               test_value DECIMAL(10,2) NOT NULL,
                                               test_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                               equipment_id INT NOT NULL,

                                               FOREIGN KEY (appointment_id)
                                                   REFERENCES appointment(appointment_id),
                                               FOREIGN KEY (equipment_id)
                                                   REFERENCES equipment(equipment_id)
) ENGINE=InnoDB;
    """
]


def get_connection_db(sql_config: dict):
    required_keys = ['user', 'password', 'database']
    for key in required_keys:
        if key not in sql_config:
            raise ValueError(f"Missing required MySQL config key: {key}")

    user = sql_config['user']
    password = sql_config['password']
    database = sql_config['database']

    host = sql_config.get('host', 'localhost')
    port = sql_config.get('port', 3306)

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    conn.autocommit = True

    # Создаем временный курсор для настройки БД
    with conn.cursor() as cursor:
        cursor.execute(SQL_CREATE_DB.format(db_name=database))
        cursor.execute(SQL_USE_DB.format(db_name=database))

        for sql_cmd in SQL_CREATE_TABLES:
            cursor.execute(sql_cmd)

    print("Схема базы данных успешно создана/обновлена")
    return conn


def execute_query(connection, query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error executing query: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")


def seed_appointments(connection):
    """Заполнение тестовых записей на приём"""
    # Получаем существующие ID
    with connection.cursor() as cursor:
        # Получаем contract_id как строковые ключи
        cursor.execute("SELECT contract_id FROM contract")
        contract_ids = [row['contract_id'] for row in cursor.fetchall()] or [None]

        # Получаем employee_id как строковые ключи
        cursor.execute("SELECT employee_id FROM employee")
        employee_ids = [row['employee_id'] for row in cursor.fetchall()]

        # Получаем cabinet_id как строковые ключи
        cursor.execute("SELECT cabinet_id FROM cabinet")
        cabinet_ids = [row['cabinet_id'] for row in cursor.fetchall()] or [None]

    # Вставляем тестовые записи
    for i in range(10):
        execute_query(
            connection,
            """INSERT INTO appointment 
            (contract_id, employee_id, cabinet_id, notes)
            VALUES (%s, %s, %s, %s)""",
            (
                random.choice(contract_ids),
                random.choice(employee_ids),
                random.choice(cabinet_ids),

                "Тестовая запись"
            )
        )


def seed_basic_data(connection):
    # Правильный порядок очистки таблиц
    tables = [
        'quality_control', 'invoice', 'appointment', 'contract',
        'purchase_item', 'purchase', 'client', 'supply_order_item',
        'supply_order', 'medicine_batch', 'medicine', 'equipment',
        'employee', 'cabinet', 'category', 'warehouse', 'supplier'
    ]

    # Очистка таблиц
    for table in tables:
        try:
            execute_query(connection, f"DELETE FROM {table}")
        except Exception as e:
            print(f"Ошибка при очистке таблицы {table}: {e}")

    # 1. Поставщики
    suppliers = [
        ('ФармаМед', 'ул. Ленина, 15', '7701234567', 'CNT-001', '12345678', '+79991234567', 'Иванов И.И.'),
        ('МедТехника', 'пр. Мира, 42', '7707654321', 'CNT-002', '87654321', '+79997654321', 'Петров П.П.')
    ]
    for s in suppliers:
        execute_query(
            connection,
            "INSERT INTO supplier (legal_name, legal_address, inn, contract_number, okpo_code, phone, contact_person) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            s
        )

    # 2. Склады
    warehouses = [
        ('Основной склад', 'ул. Складская, 1', 'Главный склад медикаментов'),
        ('Холодильный склад', 'ул. Морозная, 5', 'Склад для термочувствительных препаратов')
    ]
    for w in warehouses:
        execute_query(
            connection,
            "INSERT INTO warehouse (warehouse_name, warehouse_addr, description) VALUES (%s, %s, %s)",
            w
        )

    # 3. Категории
    categories = [
        ('Анализаторы', 'Лабораторное оборудование', False, 2),
        ('Реактивы', 'Расходные материалы', True, 100)
    ]
    for c in categories:
        execute_query(
            connection,
            "INSERT INTO category (category_name, description, is_consumable, min_stock) VALUES (%s, %s, %s, %s)",
            c
        )

    # 4. Кабинеты
    cabinets = [
        ('Кабинет 101', 'Офтальмологический кабинет'),
        ('Кабинет 205', 'Лаборатория')
    ]
    for cab in cabinets:
        execute_query(
            connection,
            "INSERT INTO cabinet (cabinet_name, description) VALUES (%s, %s)",
            cab
        )

    # 5. Сотрудники
    employees = [
        ('Сергеев А.В.', 'ул. Центральная, 10', '+79991112233', 'sergeev@clinic.ru', 'лаборант'),
        ('Козлова М.И.', 'пр. Победы, 25', '+79994445566', 'kozlova@clinic.ru', 'офтальмолог')
    ]
    for emp in employees:
        execute_query(
            connection,
            "INSERT INTO employee (full_name, address, phone, email, position) VALUES (%s, %s, %s, %s, %s)",
            emp
        )

    # 6. Оборудование (после заполнения category, warehouse, cabinet, employee)
    # Получаем ID для внешних ключей
    with connection.cursor() as cursor:
        cursor.execute("SELECT category_id FROM category")
        category_ids = [row['category_id'] for row in cursor.fetchall()]

        cursor.execute("SELECT warehouse_id FROM warehouse")
        warehouse_ids = [row['warehouse_id'] for row in cursor.fetchall()]

        cursor.execute("SELECT cabinet_id FROM cabinet")
        cabinet_ids = [row['cabinet_id'] for row in cursor.fetchall()]

        cursor.execute("SELECT employee_id FROM employee")
        employee_ids = [row['employee_id'] for row in cursor.fetchall()]

    equipment = [
        ('Анализатор BioLab-2000', category_ids[0], warehouse_ids[0], cabinet_ids[0], employee_ids[0],
         'Стеллаж А5', 365, 5, 2),
        ('Реагенты для анализа', category_ids[1], warehouse_ids[0], cabinet_ids[1], employee_ids[1],
         'Холодильник В3', 90, 150, 100)
    ]

    for eq in equipment:
        execute_query(
            connection,
            """INSERT INTO equipment 
            (equipment_name, category_id, warehouse_id, cabinet_id, employee_id, 
             shelf_location, max_shelf_life, current_stock, min_stock) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            eq
        )

    # 7. Медикаменты
    medicines = [
        ('Аспирин', 'Обезболивающее', 'таблетки', False),
        ('Инсулин', 'Гормональный препарат', 'ампулы', True)
    ]
    for med in medicines:
        execute_query(connection,
                      "INSERT INTO medicine (medicine_name, description, medicine_form, is_rx_required) "
                      "VALUES (%s, %s, %s, %s)",
                      med
                      )

    # 8. Партии медикаментов
    with connection.cursor() as cursor:
        cursor.execute("SELECT supplier_id FROM supplier")
        supplier_ids = [row['supplier_id'] for row in cursor.fetchall()]  # Исправлено здесь

        cursor.execute("SELECT warehouse_id FROM warehouse")
        warehouse_ids = [row['warehouse_id'] for row in cursor.fetchall()]

    batches = [
        (1, supplier_ids[0], warehouse_ids[0], 'BATCH-2023-001', 500, 150.0, 10.0, '2023-01-15', '2025-01-15'),
        (2, supplier_ids[1], warehouse_ids[1], 'BATCH-2023-002', 200, 450.0, 5.0, '2023-02-20', '2024-02-20')
    ]

    for batch in batches:
        execute_query(
            connection,
            """INSERT INTO medicine_batch 
            (medicine_id, supplier_id, warehouse_id, batch_number, 
             quantity_in_stock, price, social_discount, manufacture_date, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            batch
        )

    # 9. Клиенты
    clients = [
        ('Иванов П.С.', '+79998887766', 'ivanov@mail.ru', 5.0),
        ('Сидорова О.Л.', '+79995554433', 'sidorova@gmail.com', 10.0)
    ]
    for cl in clients:
        execute_query(connection,
                      "INSERT INTO client (full_name, phone, email, discount_rate) "
                      "VALUES (%s, %s, %s, %s)",
                      cl
                      )

    seed_appointments(connection)

    # 10. Контракты
    with connection.cursor() as cursor:
        cursor.execute("SELECT client_id FROM client")
        client_ids = [row['client_id'] for row in cursor.fetchall()]

    # Добавляем тестовые контракты
    contracts = []
    for client_id in client_ids:
        # По два контракта на каждого клиента
        contracts.append(
            (client_id, 'Медобслуживание', '2023-01-01', 15000.00, 'активен')
        )
        contracts.append(
            (client_id, 'Диагностика', '2023-03-10', 7500.00, 'завершен')
        )

    for contract in contracts:
        execute_query(
            connection,
            """INSERT INTO contract (client_id, service_type, contract_date, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)""",
            contract
        )

    # 11. Записи на приём (должны быть после контрактов)
    seed_appointments(connection)

    # 12. Инвойсы (пример добавления)
    with connection.cursor() as cursor:
        cursor.execute("SELECT contract_id FROM contract")
        contract_ids = [row['contract_id'] for row in cursor.fetchall()]

    for contract_id in contract_ids:
        execute_query(
            connection,
            """INSERT INTO invoice (contract_id, invoice_date, amount, is_paid, payment_date)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                contract_id,
                '2023-04-01',
                5000.00,
                True,
                '2023-04-05'
            )
        )



def seed_quality_data(connection, num_records=30):
    """Генерация тестовых данных для контроля качества"""
    # Получаем equipment_ids как целые числа
    with connection.cursor() as cursor:
        cursor.execute("SELECT equipment_id FROM equipment")
        equipment_ids = [row['equipment_id'] for row in cursor.fetchall()]  # Используем имя поля

    # Получаем appointment_ids
    with connection.cursor() as cursor:
        cursor.execute("SELECT appointment_id FROM appointment")
        appointment_data = cursor.fetchall()
        appointment_ids = [row['appointment_id'] for row in appointment_data] if appointment_data else [None]

    base_date = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        test_date = base_date + timedelta(days=i, hours=random.randint(9, 17))

        execute_query(
            connection,
            """INSERT INTO quality_control 
            (appointment_id, test_value, test_date, equipment_id)
            VALUES (%s, %s, %s, %s)""",
            (
                random.choice(appointment_ids),
                round(random.uniform(95.0, 105.0), 1),
                test_date.strftime('%Y-%m-%d %H:%M:%S'),  # Форматируем дату
                random.choice(equipment_ids)  # Теперь передается число
            )
        )

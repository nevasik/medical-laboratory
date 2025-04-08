create database free_project;

use free_project;

DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS invoice;
DROP TABLE IF EXISTS contract;
DROP TABLE IF EXISTS purchase_item;
DROP TABLE IF EXISTS purchase;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS supply_order_item;
DROP TABLE IF EXISTS supply_order;
DROP TABLE IF EXISTS medicine_batch;
DROP TABLE IF EXISTS medicine;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS cabinet;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS warehouse;
DROP TABLE IF EXISTS supplier;

-- 15 таблиц
-- 1) Справочник поставщиков
CREATE TABLE IF NOT EXISTS supplier (
                                        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                                        legal_name VARCHAR(255) NOT NULL,
                                        legal_address VARCHAR(255) NOT NULL,
                                        inn VARCHAR(20),                 -- можно добавить UNIQUE, если хотите
                                        contract_number VARCHAR(50),
                                        okpo_code VARCHAR(20),
                                        phone VARCHAR(20),
                                        contact_person VARCHAR(255)
) ENGINE=InnoDB;

-- 2) Справочник складов
CREATE TABLE IF NOT EXISTS warehouse (
                                         warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
                                         warehouse_name VARCHAR(100) NOT NULL,
                                         warehouse_addr VARCHAR(255) NOT NULL,
                                         description TEXT
) ENGINE=InnoDB;

-- 3) Справочник категорий (для оборудования/материалов)
CREATE TABLE IF NOT EXISTS category (
                                        category_id INT AUTO_INCREMENT PRIMARY KEY,
                                        category_name VARCHAR(100) NOT NULL,
                                        description TEXT,
                                        is_consumable BOOLEAN NOT NULL DEFAULT FALSE,
                                        min_stock INT
) ENGINE=InnoDB;

-- 4) Справочник кабинетов
CREATE TABLE IF NOT EXISTS cabinet (
                                       cabinet_id INT AUTO_INCREMENT PRIMARY KEY,
                                       cabinet_name VARCHAR(50) NOT NULL,
                                       description TEXT
) ENGINE=InnoDB;

-- 5) Справочник сотрудников
CREATE TABLE IF NOT EXISTS employee (
                                        employee_id INT AUTO_INCREMENT PRIMARY KEY,
                                        full_name VARCHAR(255) NOT NULL,
                                        address VARCHAR(255),
                                        phone VARCHAR(20),
                                        email VARCHAR(100),
                                        position VARCHAR(50)       -- например: "окулист", "ортопед", "бухгалтер", "фармацевт" и т.д.
) ENGINE=InnoDB;

-- 6) Справочник оборудования/материалов
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

-- 7) Справочник медикаментов (общая инфо, без учёта партий)
CREATE TABLE IF NOT EXISTS medicine (
                                        medicine_id INT AUTO_INCREMENT PRIMARY KEY,
                                        medicine_name VARCHAR(255) NOT NULL,
                                        description TEXT,
                                        medicine_form VARCHAR(50),   -- таблетки, ампулы, мазь...
                                        is_rx_required BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;

-- 8) Таблица партий медикаментов
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

-- 9) Заказы на поставку медикаментов
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

-- 10) Состав заказа (многие на многие через party / batch)
--     Используем составной PK (supply_order_id, batch_id)
CREATE TABLE IF NOT EXISTS supply_order_item (
                                                 supply_order_id INT NOT NULL,
                                                 batch_id INT NOT NULL,
                                                 ordered_qty INT NOT NULL,
                                                 delivered_qty INT,
                                                 price_at_order DECIMAL(10,2),

                                                 CONSTRAINT pk_supply_order_item
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

-- 11) Справочник клиентов
CREATE TABLE IF NOT EXISTS client (
                                      client_id INT AUTO_INCREMENT PRIMARY KEY,
                                      full_name VARCHAR(255) NOT NULL,
                                      phone VARCHAR(20),
                                      email VARCHAR(100),
                                      discount_rate DECIMAL(5,2) DEFAULT 0.00
) ENGINE=InnoDB;

-- 12) История покупок (purchase)
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

-- 12.1) Детали покупки (purchase_item)
CREATE TABLE IF NOT EXISTS purchase_item (
                                             purchase_id INT NOT NULL,
                                             batch_id INT NOT NULL,
                                             quantity INT NOT NULL,
                                             unit_price DECIMAL(10,2) NOT NULL,

                                             CONSTRAINT pk_purchase_item
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

-- 13) Договор на медицинские услуги (contract)
CREATE TABLE IF NOT EXISTS contract (
                                        contract_id INT AUTO_INCREMENT PRIMARY KEY,
                                        client_id INT NOT NULL,
                                        service_type VARCHAR(50),      -- "окулист", "ортопед" или "прочие"
                                        contract_date DATE NOT NULL,
                                        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                                        status VARCHAR(50),

                                        CONSTRAINT fk_contract_client
                                            FOREIGN KEY (client_id)
                                                REFERENCES client(client_id)
                                                ON UPDATE CASCADE
                                                ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 14) Счета по договору (invoice)
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

-- 15) Запись на приём (appointment)
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

CREATE TABLE IF NOT EXISTS patient (
                                       patient_id INT AUTO_INCREMENT PRIMARY KEY,
                                       first_name VARCHAR(100),
                                       last_name VARCHAR(100),
                                       phone VARCHAR(20),
                                       dob DATE
) ENGINE=InnoDB;


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
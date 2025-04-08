CREATE TABLE insurance_companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    inn VARCHAR(12) NOT NULL UNIQUE,
    account_number VARCHAR(20) NOT NULL,
    bik VARCHAR(9) NOT NULL
);

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    code INT NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    duration_days INT NOT NULL,
    average_deviation DECIMAL(5,2) NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    birthdate DATE NOT NULL,
    passport_series VARCHAR(4) NOT NULL,
    passport_number VARCHAR(6) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    insurance_policy_number VARCHAR(20) NOT NULL,
    insurance_policy_type VARCHAR(50) NOT NULL,
    company_id INT,
    is_archived BOOLEAN DEFAULT FALSE,
    UNIQUE (passport_series, passport_number),
    FOREIGN KEY (company_id) REFERENCES insurance_companies(company_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    creation_date DATETIME NOT NULL,
    status ENUM('pending', 'completed', 'archived') NOT NULL DEFAULT 'pending',
    completion_time_days INT,
    is_archived BOOLEAN DEFAULT FALSE,
    tube_code VARCHAR(255) UNIQUE,
    total DECIMAL(10,2),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)

);

CREATE TABLE order_services (
    order_service_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    service_id INT NOT NULL,
    status ENUM('pending', 'completed') NOT NULL DEFAULT 'pending',
    completion_time_days INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE analyzers (
    analyzer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE lab_technicians (
    lab_technician_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    last_login_ip VARCHAR(15),
    last_login_date DATETIME,
    is_archived BOOLEAN DEFAULT FALSE,
    is_researcher BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE provided_services (
    provided_service_id INT AUTO_INCREMENT PRIMARY KEY,
    order_service_id INT NOT NULL,
    lab_technician_id INT NOT NULL,
    analyzer_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    FOREIGN KEY (order_service_id) REFERENCES order_services(order_service_id),
    FOREIGN KEY (lab_technician_id) REFERENCES lab_technicians(lab_technician_id),
    FOREIGN KEY (analyzer_id) REFERENCES analyzers(analyzer_id)
);

CREATE TABLE analyzer_data (
    analyzer_data_id INT AUTO_INCREMENT PRIMARY KEY,
    provided_service_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    duration_seconds INT,
    FOREIGN KEY (provided_service_id) REFERENCES provided_services(provided_service_id)
);

CREATE TABLE lab_technician_services (
    lab_technician_id INT,
    service_id INT,
    PRIMARY KEY (lab_technician_id, service_id),
    FOREIGN KEY (lab_technician_id) REFERENCES lab_technicians(lab_technician_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE accountants (
    accountant_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    last_login_ip VARCHAR(15),
    last_login_date DATETIME,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE accountant_services (
    accountant_id INT,
    service_id INT,
    PRIMARY KEY (accountant_id, service_id),
    FOREIGN KEY (accountant_id) REFERENCES accountants(accountant_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE administrators (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    accountant_id INT NOT NULL,
    company_id INT NOT NULL,
    order_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'paid') NOT NULL DEFAULT 'pending',
    invoice_date DATETIME NOT NULL,
    FOREIGN KEY (accountant_id) REFERENCES accountants(accountant_id),
    FOREIGN KEY (company_id) REFERENCES insurance_companies(company_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE login_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL,
    success BOOLEAN NOT NULL,
    attempt_time DATETIME NOT NULL,
    role VARCHAR(50) NOT NULL
);

DELIMITER //
CREATE TRIGGER before_order_archive
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.is_archived = TRUE THEN
        IF EXISTS (
            SELECT 1 FROM order_services
            WHERE order_id = NEW.order_id AND status != 'completed'
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot archive order with pending services';
        END IF;
    END IF;
END;
//
DELIMITER ;
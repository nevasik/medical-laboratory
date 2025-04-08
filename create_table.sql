CREATE TABLE services (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code INT UNIQUE,
    name VARCHAR(255),
    cost DECIMAL(10, 2),
    result_type VARCHAR(50),
    analyzers VARCHAR(255)
);

CREATE UNIQUE INDEX idx_services_code ON services(code);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50),
    service_code INT,
    analyzer_name VARCHAR(50),
    status ENUM('pending', 'in_progress', 'sent', 'completed', 'rejected') DEFAULT 'pending',
    result TEXT,
    progress INT DEFAULT 0,
    FOREIGN KEY (service_code) REFERENCES services(code)
);

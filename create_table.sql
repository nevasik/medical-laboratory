-- create_table.sql

CREATE TABLE analyzers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    model TEXT NOT NULL,
    location TEXT
);

CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date TEXT,
    insurance_id TEXT
);

CREATE TABLE samples (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    analyzer_id INTEGER,
    test_type TEXT NOT NULL,
    result TEXT,
    status TEXT DEFAULT 'received',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (analyzer_id) REFERENCES analyzers(id)
);

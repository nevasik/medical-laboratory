class Config:
    DEBUG = False

    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '59723833',
        'database': 'medical_laboratory'
    }
    CAPTCHA_LENGTH = 4
    BLOCK_TIME_SEC = 10
    SESSION_TIMEOUT_MIN = 10
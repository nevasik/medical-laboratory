class Config:
    DEBUG = False

    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'session1'
    }
    CAPTCHA_LENGTH = 4
    BLOCK_TIME_SEC = 10
    SESSION_TIMEOUT_MIN = 10
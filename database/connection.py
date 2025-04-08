import pymysql
from config import Config
from logger import logger

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        try:
            self.connection = pymysql.connect(**Config.DB_CONFIG)
            logger.debug("Successfully connected to the database")
            return self.connection
        except pymysql.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

def get_connection():
    return pymysql.connect(**Config.DB_CONFIG)
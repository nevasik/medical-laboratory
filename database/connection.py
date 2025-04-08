import mysql.connector
from config import Config
from logger import logger

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**Config.DB_CONFIG)
            logger.debug("Successfully connected to the database")
            return self.connection
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

def get_connection():
    return mysql.connector.connect(**Config.DB_CONFIG)
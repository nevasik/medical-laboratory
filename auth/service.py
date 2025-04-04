import mysql.connector
from database import connection, queries
from utils.logger import log_error

class AuthService:
    @staticmethod
    def check_credentials(login, password):
        try:
            conn = connection.get_connection()
            cursor = conn.cursor()

            cursor.execute(queries.QUERIES['check_admin'], (login, password))
            admin = cursor.fetchone()

            cursor.execute(queries.QUERIES['check_lab_technician'], (login, password))
            lab = cursor.fetchone()

            cursor.execute(queries.QUERIES['check_accountant'], (login, password))
            accountant = cursor.fetchone()

            return admin or lab or accountant

        except mysql.connector.Error as err:
            log_error(f"Database error: {err}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def log_login_attempt(login, success, role):
        try:
            conn = connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(queries.QUERIES['log_login'], (login, success, role))
            conn.commit()
        except mysql.connector.Error as err:
            log_error(f"Login history error: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
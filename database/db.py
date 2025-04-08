from fuzzywuzzy import process
from database.connection import get_connection
import logging

logger = logging.getLogger(__name__)


def search_patients(term):
    """
    Поиск пациентов по заданному термину
    """
    try:
        with get_connection() as conn:
            if not conn:
                return []
            
            cursor = conn.cursor()
            # Обновляем запрос для получения даты рождения и номера страхового полиса
            cursor.execute("""
                SELECT patient_id, full_name, birthdate, insurance_policy_number 
                FROM patients 
                WHERE full_name LIKE %s AND is_archived = 0
                ORDER BY full_name
                LIMIT 10
            """, (f"%{term}%",))
            
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        return []

def get_services():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT service_id, name, cost FROM services WHERE is_archived = 0")
        return cursor.fetchall(), cursor.description
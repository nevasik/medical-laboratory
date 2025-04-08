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

def get_insurance_companies():
    """
    Получение списка страховых компаний
    """
    try:
        with get_connection() as conn:
            if not conn:
                logger.error("Failed to connect to database")
                return []
            
            cursor = conn.cursor()
            cursor.execute("SELECT company_id, name FROM insurance_companies WHERE is_archived = 0")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting insurance companies: {e}")
        return []

def get_insurance_types():
    """
    Получение списка типов страховых полисов
    """
    try:
        with get_connection() as conn:
            if not conn:
                logger.error("Failed to connect to database")
                return []
            
            cursor = conn.cursor()
            cursor.execute("SELECT type_id, name FROM insurance_policy_types WHERE is_archived = 0")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting insurance types: {e}")
        return []

def add_patient(data):
    """
    Добавление нового пациента
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (
                    full_name, birthdate, passport_series, passport_number,
                    phone, email, insurance_policy_number, insurance_policy_type,
                    company_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['full_name'], data['birthdate'], data['passport_series'],
                data['passport_number'], data['phone'], data['email'],
                data['insurance_policy'], data['insurance_type'],
                data['insurance_company']
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error adding patient: {e}")
        return False
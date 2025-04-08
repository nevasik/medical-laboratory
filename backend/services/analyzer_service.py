from fastapi import APIRouter, BackgroundTasks
from pymysql import MySQLError
import requests
from ..utils.database import get_db_connection
import json
import logging
from threading import Lock
from fastapi import Request

router = APIRouter()
analyzer_locks = {}
lock = Lock()


REFERENCE_VALUES = {
    619: 5.0, 311: 100.0, 548: 45.0, 258: 0.9,
    176: 20.0, 501: "negative", 543: "negative",
    557: "negative", 229: "negative", 415: 9.0,
    323: 5.0, 855: "negative", 346: 70.0, 836: 100.0,
    659: "negative", 797: "negative", 287: "negative"
}



async def process_analyzer_task(analyzer_name: str, patient_id: str, services: list):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Обновляем статус услуг
                for service in services:
                    cursor.execute("""
                        UPDATE services 
                        SET status = 'processing', analyzer_name = %s 
                        WHERE patient_id = %s AND service_code = %s
                    """, (analyzer_name, patient_id, service['serviceCode']))
                connection.commit()

                # Эмуляция работы с анализатором
                response = requests.post(
                    f"http://localhost:8000/api/analyzer/{analyzer_name}",
                    json={"patient": patient_id, "services": services}
                )

                if response.status_code == 200:
                    while True:
                        status_response = requests.get(
                            f"http://localhost:8000/api/analyzer/{analyzer_name}"
                        )
                        if status_response.json().get('progress', 100) == 100:
                            results = status_response.json()['services']
                            for result in results:
                                # Проверка отклонений
                                ref = REFERENCE_VALUES[result['code']]
                                deviation = None
                                if isinstance(ref, (int, float)):
                                    deviation = abs((float(result['result']) - ref) / ref)

                                cursor.execute("""
                                    UPDATE services 
                                    SET result = %s, deviation = %s, status = 'awaiting_approval' 
                                    WHERE patient_id = %s AND service_code = %s
                                """, (result['result'], deviation, patient_id, result['code']))
                            connection.commit()
                            break
                else:
                    logging.error(f"Analyzer error: {response.text}")

    except MySQLError as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        analyzer_locks.pop(analyzer_name, None)


@router.post("/analyzer/{analyzer_name}")
async def send_to_analyzer(
        analyzer_name: str,
        patient: str,
        services: list,
        background_tasks: BackgroundTasks
):
    if analyzer_name in analyzer_locks:
        return {"error": "Analyzer is busy"}

    analyzer_locks[analyzer_name] = True
    background_tasks.add_task(process_analyzer_task, analyzer_name, patient, services)
    return {"message": "Processing started"}


@router.get("/analyzer/{analyzer_name}")
async def get_analyzer_status(analyzer_name: str):
    try:
        # Эмуляция запроса к реальному анализатору
        response = requests.get(f"http://localhost:8000/api/analyzer/{analyzer_name}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@router.post("/service/update_status")
async def update_status(request: Request):
    data = await request.json()
    patient_id = data['patient_id']
    code = data['service_code']
    status = data['status']

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE services 
                    SET status = %s 
                    WHERE patient_id = %s AND service_code = %s
                """, (status, patient_id, code))
            conn.commit()
        return {"message": "Статус обновлён"}
    except MySQLError as e:
        return {"error": str(e)}

def get_router():
    return router

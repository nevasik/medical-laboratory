from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from backend.services.analyzer_service import router as analyzer_router
from fastapi import APIRouter
from backend.utils.database import get_db_connection
from interface_ui import report_generator
from interface_ui.report_generator import ReportGenerator
from fastapi.responses import FileResponse
import asyncio
import random

router = APIRouter()


class ServiceRequest(BaseModel):
    patient: int
    services: list[int]

class ApproveResult(BaseModel):
    approved: bool

@router.post("/analyzer/{name}")
async def send_to_analyzer(name: str, request: ServiceRequest):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT id, status FROM analyzers WHERE name = %s", (name,))
    analyzer = cursor.fetchone()
    if not analyzer or analyzer["status"] == "busy":
        raise HTTPException(status_code=400, detail="Анализатор занят или не существует")

    analyzer_id = analyzer["id"]
    cursor.execute("UPDATE analyzers SET status = 'busy' WHERE id = %s", (analyzer_id,))
    db.commit()

    for service in request.services:
        cursor.execute("""
            INSERT INTO results (patient_id, service_code, analyzer_id, status)
            VALUES (%s, %s, %s, 'pending')
        """, (request.patient, service, analyzer_id))
    db.commit()

    asyncio.create_task(process_analysis(analyzer_id, name, request.patient, request.services))
    db.close()
    return {"message": "Отправлено на анализ"}

@router.get("/analyzer/{name}")
async def get_analysis_result(name: str, patient: int):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT r.service_code, r.result_value, r.status
        FROM results r
        JOIN analyzers a ON r.analyzer_id = a.id
        WHERE a.name = %s AND r.patient_id = %s
    """, (name, patient))
    results = cursor.fetchall()
    db.close()

    if not results:
        raise HTTPException(status_code=404, detail="Результаты не найдены")

    if any(r["status"] == "pending" for r in results):
        return {"progress": random.randint(1, 99)}

    return {
        "patient": patient,
        "services": [{"code": r["service_code"], "result": r["result_value"]} for r in results]
    }

@router.get("/analyzers")
async def get_analyzers():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT name, status FROM analyzers")
    analyzers = cursor.fetchall()
    db.close()
    return analyzers

@router.get("/services/{analyzer_name}")
async def get_services(analyzer_name: str):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.code, s.name, s.result_type
        FROM services s
        JOIN service_analyzer sa ON sa.service_code = s.code
        JOIN analyzers a ON a.id = sa.analyzer_id
        WHERE a.name = %s
    """, (analyzer_name,))
    services = cursor.fetchall()
    db.close()
    return services

@router.put("/results/{result_id}")
async def approve_result(result_id: int, body: ApproveResult):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE results SET approved = %s WHERE id = %s
    """, (body.approved, result_id))
    db.commit()
    db.close()
    return {"message": "Результат подтвержден" if body.approved else "Отменено"}

@router.get("/report/pdf")
def get_pdf_report(
    insurance_company: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    path = report_generator.generate_pdf(insurance_company, start_date, end_date)
    return FileResponse(path, media_type="application/pdf", filename=path.split("/")[-1])

@router.get("/report/csv")
def get_csv_report(
    insurance_company: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    path = report_generator.generate_csv(insurance_company, start_date, end_date)
    return FileResponse(path, media_type="text/csv", filename=path.split("/")[-1])

@router.get("/services")
async def get_services_by_status(status: Optional[str] = None):
    db = get_db_connection()
    cursor = db.cursor()

    if status:
        cursor.execute("SELECT * FROM services WHERE status = %s", (status,))
    else:
        cursor.execute("SELECT * FROM services")

    services = cursor.fetchall()
    db.close()
    return services


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.get("/analyzers")
async def get_analyzers():
    # Вернёт список всех доступных анализаторов
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM analyzers")
                rows = cursor.fetchall()
                return [{"name": row[0]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services")
async def get_services(status: str, analyzer: Optional[str] = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT service_code, name, patient_id FROM services WHERE status = %s"
                params = [status]

                if analyzer:
                    query += " AND analyzer_name = %s"
                    params.append(analyzer)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [{"code": row[0], "name": row[1], "patient_id": row[2]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

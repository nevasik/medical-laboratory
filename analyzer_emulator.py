from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import threading
import time
import random

app = FastAPI()

class Service(BaseModel):
    serviceCode: int

class Order(BaseModel):
    patient: str
    services: List[Service]

# Храним состояние анализаторов
analyzers = {
    "Ledetect": {"busy": False, "services": [619, 311, 501, 543, 557, 229, 415, 323, 346, 659]},
    "Biorad": {"busy": False, "services": [619, 548, 258, 176, 543, 855, 836, 659, 797, 287]},
}

orders: Dict[str, Dict] = {}

def process_order(name, patient, services):
    analyzers[name]["busy"] = True
    progress = 0
    while progress < 100:
        orders[patient]["progress"] = progress
        time.sleep(1)
        progress += 20
    # генерируем результаты
    results = []
    for s in services:
        result = str(random.randint(1, 100)) if s["serviceCode"] < 500 else random.choice(["Negative", "Positive"])
        results.append({"code": s["serviceCode"], "result": result})
    orders[patient] = {"patient": patient, "services": results}
    analyzers[name]["busy"] = False

@app.post("/api/analyzer/{name}")
def send_order(name: str, order: Order):
    if name not in analyzers:
        raise HTTPException(status_code=400, detail=f"Analyzer with name '{name}' not found")

    analyzer = analyzers[name]
    if analyzer["busy"]:
        raise HTTPException(status_code=400, detail="Analyzer is busy")

    if not all(s.serviceCode in analyzer["services"] for s in order.services):
        raise HTTPException(status_code=400, detail="Analyzer can not do this order. May be order contains services which analyzer does not support.")

    orders[order.patient] = {"progress": 0}
    thread = threading.Thread(target=process_order, args=(name, order.patient, [s.dict() for s in order.services]))
    thread.start()
    return {"status": "Order accepted"}

@app.get("/api/analyzer/{name}")
def get_result(name: str, patient: str):
    if patient not in orders:
        raise HTTPException(status_code=400, detail="Analyzer is not working.")

    if "progress" in orders[patient]:
        return {"progress": orders[patient]["progress"]}
    return orders[patient]

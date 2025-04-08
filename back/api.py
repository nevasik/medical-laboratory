from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import random

app = FastAPI()
analyzers_state = {}

class ServiceRequest(BaseModel):
    patient: str
    services: List[dict]

class ServiceResult(BaseModel):
    patient: str
    services: List[dict]

@app.post("/api/analyzer/{name}")
async def send_to_analyzer(name: str, request: ServiceRequest):
    if name not in ["Ledetect", "Biorad"]:
        raise HTTPException(status_code=400, detail=f"Analyzer with name '{name}' not found")

    if analyzers_state.get(name, {}).get("busy"):
        raise HTTPException(status_code=400, detail="Analyzer is busy")

    unsupported_services = [s for s in request.services if not analyzer_can_handle(name, s["serviceCode"])]
    if unsupported_services:
        raise HTTPException(status_code=400, detail="Analyzer can not do this order.")

    analyzers_state[name] = {
        "busy": True,
        "patient": request.patient,
        "services": request.services,
        "progress": 0,
        "result": None
    }
    return {"message": "Order sent to analyzer."}

@app.get("/api/analyzer/{name}")
async def get_result(name: str):
    state = analyzers_state.get(name)
    if not state:
        raise HTTPException(status_code=400, detail="Analyzer is not working.")

    if state["progress"] < 100:
        state["progress"] += random.randint(10, 25)
        if state["progress"] >= 100:
            state["result"] = [
                {
                    "code": s["serviceCode"],
                    "result": str(random.randint(1, 100)) if s["serviceCode"] % 2 == 0 else "Positive"
                } for s in state["services"]
            ]
            state["busy"] = False
        return {"progress": min(state["progress"], 100)}

    return {"patient": state["patient"], "services": state["result"]}

def analyzer_can_handle(name, code):
    supported = {
        "Ledetect": [619, 311, 501, 543, 557, 229, 415, 323, 346, 659],
        "Biorad": [619, 548, 258, 176, 543, 855, 836, 797, 287, 659]
    }
    return code in supported.get(name, [])

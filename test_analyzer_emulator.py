import pytest
from fastapi.testclient import TestClient
from analyzer_emulator import app, analyzers

client = TestClient(app)

PATIENT = "test_patient"
VALID_SERVICE = {"serviceCode": 311}
INVALID_SERVICE = {"serviceCode": 999}
ANALYZER = "Ledetect"
INVALID_ANALYZER = "Unknown"

def test_invalid_analyzer_name():
    response = client.post(f"/api/analyzer/{INVALID_ANALYZER}", json={"patient": PATIENT, "services": [VALID_SERVICE]})
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]

def test_service_not_supported():
    response = client.post(f"/api/analyzer/{ANALYZER}", json={"patient": PATIENT, "services": [INVALID_SERVICE]})
    assert response.status_code == 400
    assert "can not do this order" in response.json()["detail"]

def test_successful_order():
    response = client.post(f"/api/analyzer/{ANALYZER}", json={"patient": PATIENT, "services": [VALID_SERVICE]})
    assert response.status_code == 200
    assert response.json()["status"] == "Order accepted"

def test_progress_and_result():
    import time
    time.sleep(7)  # Подождём пока обработается заказ
    response = client.get(f"/api/analyzer/{ANALYZER}?patient={PATIENT}")
    data = response.json()
    if "progress" in data:
        assert 0 <= data["progress"] <= 100
    else:
        assert isinstance(data["services"], list)

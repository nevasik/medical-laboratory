import pytest
from fastapi.testclient import TestClient
from back.api import app, analyzers_state

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_state():
    analyzers_state.clear()

def test_analyzer_busy():
    payload = {
        "patient": "123",
        "services": [{"serviceCode": 619}]
    }
    r1 = client.post("/api/analyzer/Ledetect", json=payload)
    assert r1.status_code == 200

    r2 = client.post("/api/analyzer/Ledetect", json=payload)
    assert r2.status_code == 400
    assert "Analyzer is busy" in r2.text

def test_analyzer_not_found():
    r = client.post("/api/analyzer/Nonexistent", json={"patient": "123", "services": [{"serviceCode": 619}]})
    assert r.status_code == 400
    assert "Analyzer with name 'Nonexistent' not found" in r.text

def test_service_not_supported():
    r = client.post("/api/analyzer/Ledetect", json={"patient": "123", "services": [{"serviceCode": 548}]})
    assert r.status_code == 400
    assert "Analyzer can not do this order" in r.text

def test_get_result_before_ready():
    r = client.get("/api/analyzer/Ledetect")
    assert r.status_code == 400
    assert "Analyzer is not working" in r.text

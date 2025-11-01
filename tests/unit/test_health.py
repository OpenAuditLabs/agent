from fastapi.testclient import TestClient

from src.oal_agent.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OAL Agent API"}


def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"metrics": "Not implemented yet"}

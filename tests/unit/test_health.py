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



def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"metrics": "Not implemented yet"}


def test_livez_endpoint():
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_build_info_endpoint():
    response = client.get("/build-info")
    assert response.status_code == 200
    json_response = response.json()
    assert "git_commit_sha" in json_response
    assert "git_branch" in json_response
    assert "git_tag" in json_response
    assert "build_date" in json_response

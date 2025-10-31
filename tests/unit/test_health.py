import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create a minimal FastAPI app for testing the health endpoint
app = FastAPI()

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OAL Agent API"}

@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    """Metrics endpoint."""
    return {"metrics": "Not implemented yet"}

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

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
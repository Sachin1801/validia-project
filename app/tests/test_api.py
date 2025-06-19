from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Validia API is up"}


def test_ping():
    response = client.get("/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

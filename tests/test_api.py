from fastapi import FastAPI
from fastapi.testclient import TestClient

# By importing the app, its on_startup and on_shutdown hooks are called,
# and we have access to its state.
from server import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ack": "ok"}

from starlette.testclient import TestClient

# By importing the app, its on_startup and on_shutdown hooks are called,
# and we have access to its state.
from server import app


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

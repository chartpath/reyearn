import os, sys
from os.path import dirname, join, abspath

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

from ..server import app
from starlette.testclient import TestClient


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

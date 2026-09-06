import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

module_path = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("user_service_app", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json()[0]["username"] == "alice"


def test_create_user():
    payload = {"username": "bob", "email": "bob@example.com", "role": "customer"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    assert response.json()["username"] == "bob"

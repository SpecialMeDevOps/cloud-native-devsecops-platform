import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

module_path = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("order_service_app", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_order(monkeypatch):
    class DummyResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        if url.endswith("/users/1"):
            return DummyResponse(200, {"id": 1, "username": "alice"})
        if url.endswith("/products/101"):
            return DummyResponse(200, {"id": 101, "name": "Laptop", "price": 1200.0, "stock": 25})
        return DummyResponse(404, {"detail": "not found"})

    monkeypatch.setattr(module.httpx, "get", fake_get)

    response = client.post(
        "/orders",
        json={"user_id": 1, "items": [{"product_id": 101, "quantity": 1}], "status": "pending"},
    )
    assert response.status_code == 201
    assert response.json()["total_amount"] == 1200.0

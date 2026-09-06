import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

module_path = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("product_service_app", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_product():
    payload = {"name": "Keyboard", "price": 99.99, "stock": 10}
    response = client.post("/products", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"

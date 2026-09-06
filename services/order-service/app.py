import os
from typing import Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Order Service", version="0.1.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")

orders_db: List[Dict[str, object]] = []


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]
    status: str = "pending"


class Order(OrderCreate):
    id: int
    total_amount: float


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "order-service"}


@app.get("/orders")
def list_orders() -> List[Dict[str, object]]:
    return orders_db


@app.get("/orders/{order_id}")
def get_order(order_id: int) -> Dict[str, object]:
    for order in orders_db:
        if int(order["id"]) == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate) -> Dict[str, object]:
    try:
        user_response = httpx.get(f"{USER_SERVICE_URL}/users/{payload.user_id}", timeout=5)
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="User does not exist")

        product_ids = [item.product_id for item in payload.items]
        product_total = 0.0
        for product_id in product_ids:
            product_response = httpx.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", timeout=5)
            if product_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Product {product_id} not found")
            product = product_response.json()
            product_total += float(product["price"]) * next(item.quantity for item in payload.items if item.product_id == product_id)

    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Dependency call failed: {exc}") from exc

    new_order = {
        "id": len(orders_db) + 1,
        "user_id": payload.user_id,
        "items": [item.model_dump() for item in payload.items],
        "status": payload.status,
        "total_amount": round(product_total, 2),
    }
    orders_db.append(new_order)
    return new_order


@app.get("/metrics")
def metrics() -> Dict[str, int]:
    return {"orders_total": len(orders_db), "pending_orders": sum(1 for order in orders_db if order["status"] == "pending")}

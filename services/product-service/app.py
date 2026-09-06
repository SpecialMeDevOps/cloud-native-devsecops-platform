from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Product Service", version="0.1.0")

products_db: List[Dict[str, object]] = [
    {"id": 101, "name": "Laptop", "price": 1200.0, "stock": 25},
    {"id": 102, "name": "Monitor", "price": 350.0, "stock": 40},
]


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class Product(ProductCreate):
    id: int


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "product-service"}


@app.get("/products")
def list_products() -> List[Dict[str, object]]:
    return products_db


@app.get("/products/{product_id}")
def get_product(product_id: int) -> Dict[str, object]:
    for product in products_db:
        if int(product["id"]) == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", status_code=201)
def create_product(payload: ProductCreate) -> Dict[str, object]:
    new_product = {
        "id": max((int(product["id"]) for product in products_db), default=100) + 1,
        "name": payload.name,
        "price": payload.price,
        "stock": payload.stock,
    }
    products_db.append(new_product)
    return new_product


@app.get("/metrics")
def metrics() -> Dict[str, int]:
    return {"products_total": len(products_db), "inventory_units": sum(int(product["stock"]) for product in products_db)}

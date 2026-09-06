from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="User Service", version="0.1.0")

users_db: List[Dict[str, object]] = [
    {"id": 1, "username": "alice", "email": "alice@example.com", "role": "customer"},
    {"id": 2, "username": "admin", "email": "admin@example.com", "role": "admin"},
]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=5)
    role: str = "customer"


class User(UserCreate):
    id: int


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "user-service"}


@app.get("/users")
def list_users() -> List[Dict[str, object]]:
    return users_db


@app.get("/users/{user_id}")
def get_user(user_id: int) -> Dict[str, object]:
    for user in users_db:
        if int(user["id"]) == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", status_code=201)
def create_user(payload: UserCreate) -> Dict[str, object]:
    new_user = {
        "id": max((int(user["id"]) for user in users_db), default=0) + 1,
        "username": payload.username,
        "email": payload.email,
        "role": payload.role,
    }
    users_db.append(new_user)
    return new_user


@app.get("/metrics")
def metrics() -> Dict[str, int]:
    return {"users_total": len(users_db), "last_user_id": max((int(user["id"]) for user in users_db), default=0)}

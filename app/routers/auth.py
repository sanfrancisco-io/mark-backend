import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from jose import jwt

from app.schemas import LoginRequest, TokenResponse

router = APIRouter()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    token = jwt.encode({"sub": body.username, "exp": exp}, JWT_SECRET, algorithm=ALGORITHM)
    return TokenResponse(access_token=token)

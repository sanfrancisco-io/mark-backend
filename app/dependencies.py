import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = "HS256"

_bearer = HTTPBearer()


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> None:
    try:
        jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

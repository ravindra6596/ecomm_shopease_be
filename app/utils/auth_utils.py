from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from app.config.config import settings
from app.utils.auth_dependency import verify_token


def hash_password(password: str):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )

def create_access_token(data: dict):
    payload = data.copy()
    payload["type"] = "access"
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict):
    payload = data.copy()
    payload["type"] = "refresh"
    payload["exp"] = datetime.now(timezone.utc) + timedelta(weeks=5)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_jwt_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
    except JWTError:
        return None
# Require admin
def require_admin(token_data: dict = Depends(verify_token)):
    if token_data.get("role", "") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can access this API"
        )
    return token_data
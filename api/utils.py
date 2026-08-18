from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional

from core.settings import settings


def get_model(request: Request):
    return request.app.state.model


# ╔════════════════════════════════════════════════════════════╗
# ║ 🔑 AUTHENTICATION
# ╚════════════════════════════════════════════════════════════╝


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── PASSWORD ──────────────────────────────────────────────────


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hash_password: str,
):
    return pwd_context.verify(plain_password, hash_password)


SECRET_KEY = "secret"
ALGORITHM = "HS256"

FAKE_USER = {
    "username": settings.USERNAME,
    "hashed_password": hash_password(settings.SECRET_KEY),
}

# ── USER ──────────────────────────────────────────────────


def authenticate_user(username: str, password: str) -> Optional[dict]:
    if username == FAKE_USER["username"] and verify_password(
        password, FAKE_USER["hashed_password"]
    ):
        return {"username": username}
    return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> str:

    if settings.DEMO_MODE:
        return "demo_user"

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Atuhenticate": "Bearer"},
        )
    return username


# ╔════════════════════════════════════════════════════════════╗
# ║ 🔒 SECURITY
# ╚════════════════════════════════════════════════════════════╝


def create_access_token(username: str, expires_delta: timedelta) -> str:
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        return None


def create_refresh_token(username: str, expires_delta: timedelta) -> str:
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "exp": expires}
    payload.update({"exp": expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

"""
POST /login → send a username + password
            ← get {"access_token" :"...", "token_type: "bearer"}
"""

# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝
from fastapi import APIRouter, HTTPException, status, Depends

from api.schemas import Token, RefreshTokenRequest
from api.utils import (
    create_access_token,
    verify_token,
    create_refresh_token,
    authenticate_user,
)

from core.settings import settings
from datetime import timedelta

# ╔════════════════════════════════════════════════════════════╗
# ║ 🌐 API
# ╚════════════════════════════════════════════════════════════╝
user_login = APIRouter()
refresh_token = APIRouter()


# ╔════════════════════════════════════════════════════════════╗
# ║ 🛣️ ROUTERS
# ╚════════════════════════════════════════════════════════════╝
from fastapi.security import OAuth2PasswordRequestForm

# ── LOGIN ──────────────────────────────────────────────────


@user_login.post("/login", response_model=Token, tags=["User"])
async def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user["username"],
        timedelta(
            days=settings.ACCESS_TOKEN_EXPIRE_DAYS,
        ),
    )

    refresh_token = create_refresh_token(
        user["username"],
        timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        ),
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ── TOKEN ──────────────────────────────────────────────────
@refresh_token.post("/refresh", response_model=Token, tags=["Refresh"])
async def refresh_for_access_token(refresh_token_request: RefreshTokenRequest):
    user = refresh_token_request.refresh_token

    if not verify_token(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired.",
            headers={"WWW-Atuhenticate": "Bearer"},
        )

    username = verify_token(user)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Atuhenticate": "Bearer"},
        )

    # Generate new token

    access_token = create_access_token(
        username, timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    )
    refresh_token = create_refresh_token(
        username, timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

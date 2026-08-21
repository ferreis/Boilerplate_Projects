import os

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from authentication import (
    authenticate_user,
    consume_refresh_token,
    issue_tokens,
)
from core import get_current_user
from middleware import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_COOKIE_SECURE,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


router = APIRouter(prefix="/auth", tags=["Autenticação"])
base_url = os.getenv("BASE_URL", "/api")


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=72)


def disable_cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="auth_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
        path=f"{base_url}/auth/refresh",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


@router.post("/login")
async def login(login_request: LoginRequest, response: Response) -> dict:
    disable_cache(response)
    normalized_username = login_request.username.strip()

    authenticated_user = authenticate_user(normalized_username, login_request.password)
    access_token, refresh_token = issue_tokens(authenticated_user)
    set_refresh_cookie(response, refresh_token)
    return {
        "access_token": access_token,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh")
async def refresh_access_token(request: Request, response: Response) -> dict:
    disable_cache(response)
    refresh_token = request.cookies.get("auth_refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token ausente.")

    authenticated_user = consume_refresh_token(refresh_token)
    access_token, next_refresh_token = issue_tokens(authenticated_user)
    set_refresh_cookie(response, next_refresh_token)
    return {
        "access_token": access_token,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
async def logout(response: Response) -> dict:
    disable_cache(response)
    response.delete_cookie("auth_refresh_token", path=f"{base_url}/auth/refresh")
    return {"message": "Sessão encerrada."}


@router.get("/context")
async def get_auth_context(request: Request) -> dict:
    authenticated_user = get_current_user(request)
    return {
        "user": {
            "id": authenticated_user.get("sub"),
            "username": authenticated_user.get("username"),
        },
        "roles": authenticated_user.get("roles", []),
    }

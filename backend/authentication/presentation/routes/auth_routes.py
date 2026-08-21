from fastapi import APIRouter, HTTPException, Request, Response

from authentication.application.use_cases.login import LoginUseCase
from authentication.application.use_cases.refresh_session import RefreshSessionUseCase
from authentication.domain.exceptions import (
    ExpiredTokenError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from authentication.presentation.dependencies import get_current_user
from authentication.presentation.schemas.auth_schemas import LoginRequest


def create_auth_router(
    login_use_case: LoginUseCase,
    refresh_session_use_case: RefreshSessionUseCase,
    base_url: str,
    auth_cookie_secure: bool,
    refresh_token_expire_days: int,
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Autenticação"])

    @router.post("/login")
    async def login(login_request: LoginRequest, response: Response) -> dict:
        _disable_cache(response)
        try:
            session = login_use_case.execute(
                login_request.username,
                login_request.password,
            )
        except InvalidCredentialsError as error:
            raise HTTPException(status_code=401, detail="Credenciais inválidas.") from error

        _set_refresh_cookie(
            response,
            session.refresh_token,
            base_url,
            auth_cookie_secure,
            refresh_token_expire_days,
        )
        return {
            "access_token": session.access_token,
            "expires_in": session.access_expires_in_seconds,
        }

    @router.post("/refresh")
    async def refresh_access_token(request: Request, response: Response) -> dict:
        _disable_cache(response)
        refresh_token = request.cookies.get("auth_refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token ausente.")

        try:
            session = refresh_session_use_case.execute(refresh_token)
        except ExpiredTokenError as error:
            raise HTTPException(status_code=401, detail="Refresh token expirado.") from error
        except InvalidTokenError as error:
            raise HTTPException(status_code=401, detail="Refresh token inválido.") from error

        _set_refresh_cookie(
            response,
            session.refresh_token,
            base_url,
            auth_cookie_secure,
            refresh_token_expire_days,
        )
        return {
            "access_token": session.access_token,
            "expires_in": session.access_expires_in_seconds,
        }

    @router.post("/logout")
    async def logout(response: Response) -> dict:
        _disable_cache(response)
        response.delete_cookie(
            "auth_refresh_token",
            path=f"{base_url}/auth/refresh",
        )
        return {"message": "Sessão encerrada."}

    @router.get("/context")
    async def get_auth_context(request: Request) -> dict:
        authenticated_user = get_current_user(request)
        return {
            "user": {
                "id": authenticated_user.identifier,
                "username": authenticated_user.username,
            },
            "roles": list(authenticated_user.roles),
        }

    return router


def _disable_cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _set_refresh_cookie(
    response: Response,
    refresh_token: str,
    base_url: str,
    auth_cookie_secure: bool,
    refresh_token_expire_days: int,
) -> None:
    response.set_cookie(
        key="auth_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=auth_cookie_secure,
        samesite="lax",
        path=f"{base_url}/auth/refresh",
        max_age=refresh_token_expire_days * 86400,
    )

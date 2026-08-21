import hmac
import os
import uuid
from datetime import timedelta

import bcrypt
import jwt
from fastapi import HTTPException

from middleware import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_token,
    decode_token,
)


def validate_authentication_configuration() -> None:
    username = (os.getenv("AUTH_USERNAME") or "").strip()
    password_hash = (os.getenv("AUTH_PASSWORD_HASH") or "").strip()

    if not username:
        raise RuntimeError("AUTH_USERNAME deve ser configurado.")
    if len(username) > 120:
        raise RuntimeError("AUTH_USERNAME deve ter no máximo 120 caracteres.")
    if not password_hash.startswith("$2"):
        raise RuntimeError("AUTH_PASSWORD_HASH deve conter um hash bcrypt válido.")


def _configured_roles() -> list[str]:
    configured_roles = os.getenv("AUTH_USER_ROLES", "authenticated")
    roles = [role.strip() for role in configured_roles.split(",") if role.strip()]
    return roles or ["authenticated"]


def authenticate_user(username: str, password: str) -> dict:
    configured_username = (os.getenv("AUTH_USERNAME") or "").strip()
    configured_password_hash = (os.getenv("AUTH_PASSWORD_HASH") or "").strip()
    normalized_username = (username or "").strip()

    if not normalized_username or not password or len(password) > 72:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    username_matches = hmac.compare_digest(normalized_username, configured_username)
    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            configured_password_hash.encode("utf-8"),
        )
    except ValueError:
        password_matches = False

    if not username_matches or not password_matches:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    return {"username": configured_username, "roles": _configured_roles()}


def _token_claims(user: dict, refresh_identifier: str | None = None) -> dict:
    claims = {
        "sub": user["username"],
        "username": user["username"],
        "roles": user["roles"],
    }
    if refresh_identifier:
        claims["jti"] = refresh_identifier
    return claims


def issue_tokens(user: dict) -> tuple[str, str]:
    access_token = create_token(
        _token_claims(user),
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )
    refresh_token = create_token(
        _token_claims(user, str(uuid.uuid4())),
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )
    return access_token, refresh_token


def consume_refresh_token(refresh_token: str) -> dict:
    try:
        token_payload = decode_token(refresh_token, "refresh")
        refresh_identifier = str(token_payload.get("jti") or "").strip()
        uuid.UUID(refresh_identifier)
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(status_code=401, detail="Refresh token expirado.") from error
    except (jwt.InvalidTokenError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Refresh token inválido.") from error

    token_username = str(token_payload.get("username") or "").strip()
    configured_username = (os.getenv("AUTH_USERNAME") or "").strip()

    if not token_username or not hmac.compare_digest(token_username, configured_username):
        raise HTTPException(status_code=401, detail="Refresh token inválido.")

    return {
        "username": token_username,
        "roles": token_payload.get("roles", []),
    }

import hashlib
import hmac
import os
import uuid
from datetime import timedelta

import bcrypt
import jwt
from fastapi import HTTPException
from redis.exceptions import RedisError

from core import redis_client
from middleware import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_token,
    decode_token,
)


LOGIN_RATE_LIMIT = int(os.getenv("LOGIN_RATE_LIMIT", "5"))
LOGIN_RATE_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_WINDOW_SECONDS", "900"))


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


def _rate_limit_key(identifier: str) -> str:
    identifier_hash = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
    return f"auth:rate-limit:login:{identifier_hash}"


def enforce_login_rate_limit(identifier: str) -> None:
    try:
        rate_limit_key = _rate_limit_key(identifier)
        attempts = redis_client.incr(rate_limit_key)
        if attempts == 1:
            redis_client.expire(rate_limit_key, LOGIN_RATE_WINDOW_SECONDS)
    except RedisError as error:
        raise HTTPException(
            status_code=503,
            detail="Serviço de autenticação temporariamente indisponível.",
        ) from error

    if attempts > LOGIN_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas. Tente novamente mais tarde.",
        )


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
    refresh_identifier = str(uuid.uuid4())
    try:
        redis_client.setex(
            f"auth:refresh:{refresh_identifier}",
            REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            user["username"],
        )
    except RedisError as error:
        raise HTTPException(
            status_code=503,
            detail="Serviço de autenticação temporariamente indisponível.",
        ) from error

    access_token = create_token(
        _token_claims(user),
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )
    refresh_token = create_token(
        _token_claims(user, refresh_identifier),
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )
    return access_token, refresh_token


def consume_refresh_token(refresh_token: str) -> dict:
    try:
        token_payload = decode_token(refresh_token, "refresh")
        refresh_identifier = str(token_payload.get("jti") or "").strip()
        uuid.UUID(refresh_identifier)
        registered_username = redis_client.getdel(f"auth:refresh:{refresh_identifier}")
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(status_code=401, detail="Refresh token expirado.") from error
    except (jwt.InvalidTokenError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Refresh token inválido.") from error
    except RedisError as error:
        raise HTTPException(
            status_code=503,
            detail="Serviço de autenticação temporariamente indisponível.",
        ) from error

    token_username = str(token_payload.get("username") or "").strip()
    if not registered_username or not hmac.compare_digest(registered_username, token_username):
        raise HTTPException(status_code=401, detail="Refresh token inválido.")

    return {
        "username": token_username,
        "roles": token_payload.get("roles", []),
    }


def revoke_refresh_token(refresh_token: str | None) -> None:
    if not refresh_token:
        return

    try:
        token_payload = decode_token(refresh_token, "refresh")
        refresh_identifier = str(token_payload.get("jti") or "").strip()
        uuid.UUID(refresh_identifier)
        redis_client.delete(f"auth:refresh:{refresh_identifier}")
    except (jwt.InvalidTokenError, RedisError, ValueError):
        return

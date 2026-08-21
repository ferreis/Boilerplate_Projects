import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _get_jwt_secret() -> str:
    jwt_secret = (os.getenv("JWT_SECRET") or "").strip()
    insecure_secrets = {
        "",
        "supersecretjwtkey_change_in_production",
        "change-me-with-a-long-random-secret",
    }
    if jwt_secret in insecure_secrets or len(jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET deve ser configurado com um valor aleatório de pelo menos 32 caracteres."
        )
    return jwt_secret


JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "backend-base")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "2"))
AUTH_COOKIE_SECURE = _env_bool("AUTH_COOKIE_SECURE", True)
APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "1048576"))


def validate_security_configuration() -> None:
    _get_jwt_secret()

    if APP_ENV == "production" and not AUTH_COOKIE_SECURE:
        raise RuntimeError("AUTH_COOKIE_SECURE deve estar habilitado em produção.")

    if MAX_REQUEST_BODY_BYTES < 1024:
        raise RuntimeError("MAX_REQUEST_BODY_BYTES deve ser de pelo menos 1024 bytes.")


def create_token(
    claims: dict,
    expires_delta: timedelta,
    token_type: str,
) -> str:
    token_payload = claims.copy()
    token_payload.update(
        {
            "exp": datetime.now(timezone.utc) + expires_delta,
            "iss": JWT_ISSUER,
            "token_type": token_type,
        }
    )
    return jwt.encode(token_payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


def create_access_token(claims: dict, expires_delta: timedelta | None = None) -> str:
    token_expiration = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(claims, token_expiration, "access")


def decode_token(access_token: str, expected_token_type: str) -> dict:
    payload = jwt.decode(
        access_token,
        _get_jwt_secret(),
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
    )
    if payload.get("token_type") != expected_token_type:
        raise jwt.InvalidTokenError("Tipo de token inválido.")
    return payload


def decode_access_token(access_token: str) -> dict:
    return decode_token(access_token, "access")


async def request_size_limit_middleware(request: Request, call_next):
    content_length = request.headers.get("Content-Length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_REQUEST_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Corpo da requisição muito grande."})
    return await call_next(request)


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


async def jwt_middleware(request: Request, call_next):
    authorization_header = request.headers.get("Authorization", "").strip()

    if not authorization_header:
        return await call_next(request)

    authorization_parts = authorization_header.split(" ", 1)
    if len(authorization_parts) != 2 or authorization_parts[0].lower() != "bearer":
        return JSONResponse(status_code=401, content={"detail": "Access token inválido."})

    access_token = authorization_parts[1].strip()
    if not access_token:
        return JSONResponse(status_code=401, content={"detail": "Access token ausente."})

    try:
        request.state.user = decode_access_token(access_token)
    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Autenticação não está configurada."},
        )
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "Access token expirado."})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Access token inválido."})

    return await call_next(request)

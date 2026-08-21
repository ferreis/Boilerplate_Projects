import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv()

from middleware import (
    jwt_middleware,
    request_size_limit_middleware,
    security_headers_middleware,
    validate_security_configuration,
)
from authentication import validate_authentication_configuration
from routes import auth, health


def get_allowed_cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]

    if "*" in allowed_origins:
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS não pode usar '*' quando credenciais estão habilitadas."
        )

    return allowed_origins


base_url = os.getenv("BASE_URL", "/api")
validate_security_configuration()
validate_authentication_configuration()
app = FastAPI(
    title=os.getenv("APP_NAME", "Backend Base"),
    root_path=base_url,
)

allowed_cors_origins = get_allowed_cors_origins()
if allowed_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

trusted_hosts = [
    host.strip()
    for host in os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
if trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

app.middleware("http")(jwt_middleware)
app.middleware("http")(request_size_limit_middleware)
app.middleware("http")(security_headers_middleware)

app.include_router(health.router)
app.include_router(auth.router)

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv()

from authentication.application.use_cases.login import LoginUseCase
from authentication.application.use_cases.refresh_session import RefreshSessionUseCase
from authentication.infrastructure.providers.environment_credentials_provider import (
    EnvironmentCredentialsProvider,
)
from authentication.infrastructure.security.bcrypt_password_verifier import (
    BcryptPasswordVerifier,
)
from authentication.infrastructure.security.jwt_token_service import JwtTokenService
from authentication.presentation.middleware import create_jwt_middleware
from authentication.presentation.routes.auth_routes import create_auth_router
from shared.infrastructure.config.settings import load_settings, validate_settings
from shared.presentation.middleware.security import (
    create_request_size_limit_middleware,
    create_security_headers_middleware,
)
from system.presentation.routes.health_routes import router as health_router


settings = load_settings()
validate_settings(settings)

credentials_provider = EnvironmentCredentialsProvider(settings.authentication)
password_verifier = BcryptPasswordVerifier()
token_service = JwtTokenService(settings.authentication)

login_use_case = LoginUseCase(
    credentials_provider=credentials_provider,
    password_verifier=password_verifier,
    token_service=token_service,
)
refresh_session_use_case = RefreshSessionUseCase(
    credentials_provider=credentials_provider,
    token_service=token_service,
)

app = FastAPI(
    title=settings.app_name,
    root_path=settings.base_url,
)

if settings.cors_allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

if settings.trusted_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(settings.trusted_hosts),
    )

app.middleware("http")(create_jwt_middleware(token_service))
app.middleware("http")(
    create_request_size_limit_middleware(settings.max_request_body_bytes)
)
app.middleware("http")(create_security_headers_middleware(settings.app_env))

app.include_router(health_router)
app.include_router(
    create_auth_router(
        login_use_case=login_use_case,
        refresh_session_use_case=refresh_session_use_case,
        base_url=settings.base_url,
        auth_cookie_secure=settings.authentication.auth_cookie_secure,
        refresh_token_expire_days=(
            settings.authentication.refresh_token_expire_days
        ),
    )
)

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticationSettings:
    username: str
    password_hash: str
    roles: tuple[str, ...]
    jwt_secret: str
    jwt_algorithm: str
    jwt_issuer: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    auth_cookie_secure: bool


@dataclass(frozen=True, slots=True)
class ApplicationSettings:
    app_name: str
    app_env: str
    base_url: str
    trusted_hosts: tuple[str, ...]
    cors_allowed_origins: tuple[str, ...]
    max_request_body_bytes: int
    authentication: AuthenticationSettings


def load_settings() -> ApplicationSettings:
    configured_roles = _split_csv(os.getenv("AUTH_USER_ROLES", "authenticated"))
    roles = configured_roles or ("authenticated",)

    authentication = AuthenticationSettings(
        username=(os.getenv("AUTH_USERNAME") or "").strip(),
        password_hash=(os.getenv("AUTH_PASSWORD_HASH") or "").strip(),
        roles=roles,
        jwt_secret=(os.getenv("JWT_SECRET") or "").strip(),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_issuer=os.getenv("JWT_ISSUER", "backend-base"),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        ),
        refresh_token_expire_days=int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "2")
        ),
        auth_cookie_secure=_env_bool("AUTH_COOKIE_SECURE", True),
    )

    return ApplicationSettings(
        app_name=os.getenv("APP_NAME", "Backend Base"),
        app_env=os.getenv("APP_ENV", "production").strip().lower(),
        base_url=os.getenv("BASE_URL", "/api"),
        trusted_hosts=_split_csv(
            os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1")
        ),
        cors_allowed_origins=_split_csv(os.getenv("CORS_ALLOWED_ORIGINS", "")),
        max_request_body_bytes=int(
            os.getenv("MAX_REQUEST_BODY_BYTES", "1048576")
        ),
        authentication=authentication,
    )


def validate_settings(settings: ApplicationSettings) -> None:
    authentication = settings.authentication

    if not authentication.username:
        raise RuntimeError("AUTH_USERNAME deve ser configurado.")
    if len(authentication.username) > 120:
        raise RuntimeError("AUTH_USERNAME deve ter no máximo 120 caracteres.")
    if not authentication.password_hash.startswith("$2"):
        raise RuntimeError("AUTH_PASSWORD_HASH deve conter um hash bcrypt válido.")

    insecure_secrets = {
        "",
        "supersecretjwtkey_change_in_production",
        "change-me-with-a-long-random-secret",
    }
    if (
        authentication.jwt_secret in insecure_secrets
        or len(authentication.jwt_secret) < 32
    ):
        raise RuntimeError(
            "JWT_SECRET deve ser configurado com um valor aleatório de pelo menos 32 caracteres."
        )

    if settings.app_env == "production" and not authentication.auth_cookie_secure:
        raise RuntimeError("AUTH_COOKIE_SECURE deve estar habilitado em produção.")

    if settings.max_request_body_bytes < 1024:
        raise RuntimeError(
            "MAX_REQUEST_BODY_BYTES deve ser de pelo menos 1024 bytes."
        )

    if "*" in settings.cors_allowed_origins:
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS não pode usar '*' quando credenciais estão habilitadas."
        )


def _split_csv(raw_value: str) -> tuple[str, ...]:
    return tuple(
        value.strip()
        for value in raw_value.split(",")
        if value.strip()
    )


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}

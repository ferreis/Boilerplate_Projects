import unittest

from shared.infrastructure.config.settings import (
    ApplicationSettings,
    AuthenticationSettings,
    validate_settings,
)


def valid_settings() -> ApplicationSettings:
    authentication = AuthenticationSettings(
        username="admin",
        password_hash="$2b$12$hash",
        roles=("authenticated",),
        jwt_secret="chave-de-teste-com-mais-de-trinta-e-dois-caracteres",
        jwt_algorithm="HS256",
        jwt_issuer="backend",
        access_token_expire_minutes=15,
        refresh_token_expire_days=2,
        auth_cookie_secure=True,
    )
    return ApplicationSettings(
        app_name="Backend",
        app_env="production",
        base_url="/api",
        trusted_hosts=("localhost",),
        cors_allowed_origins=(),
        max_request_body_bytes=1048576,
        authentication=authentication,
    )


class SettingsValidationTestCase(unittest.TestCase):
    def test_valid_settings_are_accepted(self) -> None:
        validate_settings(valid_settings())

    def test_insecure_cookie_is_rejected_in_production(self) -> None:
        settings = valid_settings()
        authentication = AuthenticationSettings(
            username=settings.authentication.username,
            password_hash=settings.authentication.password_hash,
            roles=settings.authentication.roles,
            jwt_secret=settings.authentication.jwt_secret,
            jwt_algorithm=settings.authentication.jwt_algorithm,
            jwt_issuer=settings.authentication.jwt_issuer,
            access_token_expire_minutes=settings.authentication.access_token_expire_minutes,
            refresh_token_expire_days=settings.authentication.refresh_token_expire_days,
            auth_cookie_secure=False,
        )
        invalid = ApplicationSettings(
            app_name=settings.app_name,
            app_env=settings.app_env,
            base_url=settings.base_url,
            trusted_hosts=settings.trusted_hosts,
            cors_allowed_origins=settings.cors_allowed_origins,
            max_request_body_bytes=settings.max_request_body_bytes,
            authentication=authentication,
        )

        with self.assertRaisesRegex(RuntimeError, "AUTH_COOKIE_SECURE"):
            validate_settings(invalid)

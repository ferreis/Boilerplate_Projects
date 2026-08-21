import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from authentication.application.interfaces.authentication_ports import StoredCredentials
from authentication.application.use_cases.login import LoginUseCase
from authentication.application.use_cases.refresh_session import RefreshSessionUseCase
from authentication.infrastructure.security.jwt_token_service import JwtTokenService
from authentication.presentation.middleware import create_jwt_middleware
from authentication.presentation.routes.auth_routes import create_auth_router
from shared.infrastructure.config.settings import (
    ApplicationSettings,
    AuthenticationSettings,
)


class StubCredentialsProvider:
    def get_credentials(self) -> StoredCredentials:
        return StoredCredentials(
            username="admin",
            password_hash="hash",
            roles=("authenticated",),
        )


class StubPasswordVerifier:
    def verify(self, password: str, password_hash: str) -> bool:
        return password == "senha-de-teste" and password_hash == "hash"


def build_settings() -> ApplicationSettings:
    authentication = AuthenticationSettings(
        username="admin",
        password_hash="hash",
        roles=("authenticated",),
        jwt_secret="chave-de-teste-com-mais-de-trinta-e-dois-caracteres",
        jwt_algorithm="HS256",
        jwt_issuer="test-backend",
        access_token_expire_minutes=15,
        refresh_token_expire_days=2,
        auth_cookie_secure=False,
    )
    return ApplicationSettings(
        app_name="Test Backend",
        app_env="development",
        base_url="/api",
        trusted_hosts=("testserver",),
        cors_allowed_origins=(),
        max_request_body_bytes=1048576,
        authentication=authentication,
    )


class AuthenticationRoutesIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        settings = build_settings()
        credentials_provider = StubCredentialsProvider()
        token_service = JwtTokenService(settings.authentication)
        login_use_case = LoginUseCase(
            credentials_provider,
            StubPasswordVerifier(),
            token_service,
        )
        refresh_use_case = RefreshSessionUseCase(
            credentials_provider,
            token_service,
        )

        app = FastAPI()
        app.middleware("http")(create_jwt_middleware(token_service))
        app.include_router(
            create_auth_router(
                login_use_case,
                refresh_use_case,
                base_url=settings.base_url,
                auth_cookie_secure=settings.authentication.auth_cookie_secure,
                refresh_token_expire_days=(
                    settings.authentication.refresh_token_expire_days
                ),
            )
        )
        self.client = TestClient(app)

    def test_login_refresh_context_and_logout_contracts(self) -> None:
        login_response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "senha-de-teste"},
        )
        self.assertEqual(200, login_response.status_code)
        self.assertEqual(900, login_response.json()["expires_in"])
        access_token = login_response.json()["access_token"]
        self.assertTrue(access_token)
        self.assertIn("auth_refresh_token", self.client.cookies)
        self.assertEqual("no-store", login_response.headers["cache-control"])
        self.assertEqual("no-cache", login_response.headers["pragma"])
        set_cookie = login_response.headers["set-cookie"]
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("SameSite=lax", set_cookie)
        self.assertIn("Path=/api/auth/refresh", set_cookie)
        self.assertIn("Max-Age=172800", set_cookie)

        context_response = self.client.get(
            "/auth/context",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(200, context_response.status_code)
        self.assertEqual(
            {
                "user": {"id": "admin", "username": "admin"},
                "roles": ["authenticated"],
            },
            context_response.json(),
        )

        refresh_token = login_response.cookies.get("auth_refresh_token")
        refresh_response = self.client.post(
            "/auth/refresh",
            headers={"Cookie": f"auth_refresh_token={refresh_token}"},
        )
        self.assertEqual(200, refresh_response.status_code)
        self.assertEqual(900, refresh_response.json()["expires_in"])

        logout_response = self.client.post("/auth/logout")
        self.assertEqual(200, logout_response.status_code)
        self.assertEqual({"message": "Sessão encerrada."}, logout_response.json())

    def test_missing_context_authentication_is_rejected(self) -> None:
        response = self.client.get("/auth/context")
        self.assertEqual(401, response.status_code)
        self.assertEqual(
            {"detail": "Autenticação obrigatória."},
            response.json(),
        )

    def test_malformed_authorization_header_is_rejected(self) -> None:
        response = self.client.get(
            "/auth/context",
            headers={"Authorization": "Token abc"},
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "Access token inválido."}, response.json())

    def test_login_schema_preserves_password_limit(self) -> None:
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "x" * 73},
        )
        self.assertEqual(422, response.status_code)

    def test_invalid_login_is_rejected(self) -> None:
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "incorreta"},
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "Credenciais inválidas."}, response.json())

import unittest

from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.exceptions import InvalidTokenError
from authentication.infrastructure.security.jwt_token_service import JwtTokenService
from shared.infrastructure.config.settings import AuthenticationSettings


def build_settings() -> AuthenticationSettings:
    return AuthenticationSettings(
        username="admin",
        password_hash="$2b$12$hash",
        roles=("authenticated",),
        jwt_secret="chave-de-teste-com-mais-de-trinta-e-dois-caracteres",
        jwt_algorithm="HS256",
        jwt_issuer="test-backend",
        access_token_expire_minutes=15,
        refresh_token_expire_days=2,
        auth_cookie_secure=False,
    )


class JwtTokenServiceTestCase(unittest.TestCase):
    def test_access_and_refresh_tokens_preserve_user(self) -> None:
        service = JwtTokenService(build_settings())
        user = AuthenticatedUser("admin", ("authenticated",), "admin")

        session = service.issue_session(user)
        access_user = service.decode_access_token(session.access_token)
        refresh_user = service.decode_refresh_token(session.refresh_token)

        self.assertEqual("admin", access_user.username)
        self.assertEqual(("authenticated",), access_user.roles)
        self.assertEqual("admin", refresh_user.username)

    def test_refresh_tokens_are_unique(self) -> None:
        service = JwtTokenService(build_settings())
        user = AuthenticatedUser("admin", ("authenticated",), "admin")

        first = service.issue_session(user)
        second = service.issue_session(user)

        self.assertNotEqual(first.refresh_token, second.refresh_token)

    def test_access_token_cannot_be_used_as_refresh_token(self) -> None:
        service = JwtTokenService(build_settings())
        user = AuthenticatedUser("admin", ("authenticated",), "admin")
        session = service.issue_session(user)

        with self.assertRaises(InvalidTokenError):
            service.decode_refresh_token(session.access_token)

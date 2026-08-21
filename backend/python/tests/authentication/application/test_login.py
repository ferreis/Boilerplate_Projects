import unittest

from authentication.application.dto.session import SessionTokens
from authentication.application.interfaces.authentication_ports import StoredCredentials
from authentication.application.use_cases.login import LoginUseCase
from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.exceptions import InvalidCredentialsError


class StubCredentialsProvider:
    def get_credentials(self) -> StoredCredentials:
        return StoredCredentials(
            username="admin",
            password_hash="hash",
            roles=("authenticated",),
        )


class StubPasswordVerifier:
    def __init__(self, matches: bool) -> None:
        self.matches = matches

    def verify(self, password: str, password_hash: str) -> bool:
        return self.matches and password == "senha-de-teste" and password_hash == "hash"


class StubTokenService:
    def issue_session(self, user: AuthenticatedUser) -> SessionTokens:
        return SessionTokens("access", "refresh", 900)

    def decode_access_token(self, access_token: str) -> AuthenticatedUser:
        raise NotImplementedError

    def decode_refresh_token(self, refresh_token: str) -> AuthenticatedUser:
        raise NotImplementedError


class LoginUseCaseTestCase(unittest.TestCase):
    def test_valid_credentials_create_session(self) -> None:
        use_case = LoginUseCase(
            StubCredentialsProvider(),
            StubPasswordVerifier(True),
            StubTokenService(),
        )

        session = use_case.execute(" admin ", "senha-de-teste")

        self.assertEqual("access", session.access_token)
        self.assertEqual("refresh", session.refresh_token)
        self.assertEqual(900, session.access_expires_in_seconds)

    def test_invalid_password_is_rejected(self) -> None:
        use_case = LoginUseCase(
            StubCredentialsProvider(),
            StubPasswordVerifier(False),
            StubTokenService(),
        )

        with self.assertRaises(InvalidCredentialsError):
            use_case.execute("admin", "senha-incorreta")

    def test_password_over_bcrypt_limit_is_rejected(self) -> None:
        use_case = LoginUseCase(
            StubCredentialsProvider(),
            StubPasswordVerifier(True),
            StubTokenService(),
        )

        with self.assertRaises(InvalidCredentialsError):
            use_case.execute("admin", "x" * 73)

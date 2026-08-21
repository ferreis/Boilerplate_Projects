import unittest

from authentication.application.dto.session import SessionTokens
from authentication.application.interfaces.authentication_ports import StoredCredentials
from authentication.application.use_cases.refresh_session import RefreshSessionUseCase
from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.exceptions import InvalidTokenError


class StubCredentialsProvider:
    def get_credentials(self) -> StoredCredentials:
        return StoredCredentials(
            username="admin",
            password_hash="hash",
            roles=("authenticated",),
        )


class StubTokenService:
    def __init__(self, decoded_user: AuthenticatedUser) -> None:
        self.decoded_user = decoded_user

    def issue_session(self, user: AuthenticatedUser) -> SessionTokens:
        return SessionTokens("new-access", "new-refresh", 900)

    def decode_access_token(self, access_token: str) -> AuthenticatedUser:
        raise NotImplementedError

    def decode_refresh_token(self, refresh_token: str) -> AuthenticatedUser:
        return self.decoded_user


class RefreshSessionUseCaseTestCase(unittest.TestCase):
    def test_valid_refresh_token_creates_new_session(self) -> None:
        token_service = StubTokenService(
            AuthenticatedUser("admin", ("authenticated",), "admin")
        )
        use_case = RefreshSessionUseCase(StubCredentialsProvider(), token_service)

        session = use_case.execute("refresh-token")

        self.assertEqual("new-access", session.access_token)
        self.assertEqual("new-refresh", session.refresh_token)

    def test_token_for_different_user_is_rejected(self) -> None:
        token_service = StubTokenService(
            AuthenticatedUser("outro", ("authenticated",), "outro")
        )
        use_case = RefreshSessionUseCase(StubCredentialsProvider(), token_service)

        with self.assertRaises(InvalidTokenError):
            use_case.execute("refresh-token")

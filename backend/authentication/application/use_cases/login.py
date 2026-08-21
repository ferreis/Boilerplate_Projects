import hmac

from authentication.application.dto.session import SessionTokens
from authentication.application.interfaces.authentication_ports import CredentialsProvider
from authentication.application.interfaces.authentication_ports import PasswordVerifier
from authentication.application.interfaces.authentication_ports import TokenService
from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.exceptions import InvalidCredentialsError


class LoginUseCase:
    def __init__(
        self,
        credentials_provider: CredentialsProvider,
        password_verifier: PasswordVerifier,
        token_service: TokenService,
    ) -> None:
        self._credentials_provider = credentials_provider
        self._password_verifier = password_verifier
        self._token_service = token_service

    def execute(self, username: str, password: str) -> SessionTokens:
        credentials = self._credentials_provider.get_credentials()
        normalized_username = (username or "").strip()

        if not normalized_username or not password or len(password) > 72:
            raise InvalidCredentialsError

        username_matches = hmac.compare_digest(
            normalized_username,
            credentials.username,
        )
        password_matches = self._password_verifier.verify(
            password,
            credentials.password_hash,
        )

        if not username_matches or not password_matches:
            raise InvalidCredentialsError

        user = AuthenticatedUser(
            username=credentials.username,
            roles=credentials.roles,
            subject=credentials.username,
        )
        return self._token_service.issue_session(user)

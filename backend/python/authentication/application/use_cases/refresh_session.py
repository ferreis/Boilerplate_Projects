import hmac

from authentication.application.dto.session import SessionTokens
from authentication.application.interfaces.authentication_ports import CredentialsProvider
from authentication.application.interfaces.authentication_ports import TokenService
from authentication.domain.exceptions import InvalidTokenError


class RefreshSessionUseCase:
    def __init__(
        self,
        credentials_provider: CredentialsProvider,
        token_service: TokenService,
    ) -> None:
        self._credentials_provider = credentials_provider
        self._token_service = token_service

    def execute(self, refresh_token: str) -> SessionTokens:
        user = self._token_service.decode_refresh_token(refresh_token)
        credentials = self._credentials_provider.get_credentials()

        if not user.username or not hmac.compare_digest(
            user.username,
            credentials.username,
        ):
            raise InvalidTokenError

        return self._token_service.issue_session(user)

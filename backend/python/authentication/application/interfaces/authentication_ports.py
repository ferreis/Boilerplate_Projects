from dataclasses import dataclass
from typing import Protocol

from authentication.application.dto.session import SessionTokens
from authentication.domain.entities.authenticated_user import AuthenticatedUser


@dataclass(frozen=True, slots=True)
class StoredCredentials:
    username: str
    password_hash: str
    roles: tuple[str, ...]


class CredentialsProvider(Protocol):
    def get_credentials(self) -> StoredCredentials:
        ...


class PasswordVerifier(Protocol):
    def verify(self, password: str, password_hash: str) -> bool:
        ...


class TokenService(Protocol):
    def issue_session(self, user: AuthenticatedUser) -> SessionTokens:
        ...

    def decode_access_token(self, access_token: str) -> AuthenticatedUser:
        ...

    def decode_refresh_token(self, refresh_token: str) -> AuthenticatedUser:
        ...

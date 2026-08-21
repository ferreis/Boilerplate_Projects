from authentication.application.interfaces.authentication_ports import StoredCredentials
from shared.infrastructure.config.settings import AuthenticationSettings


class EnvironmentCredentialsProvider:
    def __init__(self, settings: AuthenticationSettings) -> None:
        self._settings = settings

    def get_credentials(self) -> StoredCredentials:
        return StoredCredentials(
            username=self._settings.username,
            password_hash=self._settings.password_hash,
            roles=self._settings.roles,
        )

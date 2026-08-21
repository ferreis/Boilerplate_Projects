from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    username: str
    roles: tuple[str, ...]
    subject: str | None = None

    @property
    def identifier(self) -> str:
        return self.subject or self.username

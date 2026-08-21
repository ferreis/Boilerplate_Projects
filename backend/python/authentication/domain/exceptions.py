class AuthenticationError(Exception):
    """Base exception for authentication domain failures."""


class InvalidCredentialsError(AuthenticationError):
    pass


class InvalidTokenError(AuthenticationError):
    pass


class ExpiredTokenError(InvalidTokenError):
    pass

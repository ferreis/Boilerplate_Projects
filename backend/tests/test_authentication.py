import os
import unittest

import bcrypt

os.environ.setdefault(
    "JWT_SECRET",
    "chave-de-teste-com-mais-de-trinta-e-dois-caracteres",
)
os.environ.setdefault("AUTH_USERNAME", "admin")
os.environ.setdefault(
    "AUTH_PASSWORD_HASH",
    bcrypt.hashpw(b"senha-de-teste", bcrypt.gensalt()).decode("utf-8"),
)

import authentication


class FakeRedis:
    def __init__(self):
        self.values: dict[str, str] = {}
        self.counters: dict[str, int] = {}

    def setex(self, key: str, seconds: int, value: str) -> None:
        del seconds
        self.values[key] = value

    def getdel(self, key: str) -> str | None:
        return self.values.pop(key, None)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)

    def incr(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key: str, seconds: int) -> None:
        del key, seconds


class AuthenticationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fake_redis = FakeRedis()
        self.previous_redis_client = authentication.redis_client
        authentication.redis_client = self.fake_redis

    def tearDown(self) -> None:
        authentication.redis_client = self.previous_redis_client

    def test_valid_username_and_password_are_authenticated(self) -> None:
        authenticated_user = authentication.authenticate_user("admin", "senha-de-teste")

        self.assertEqual("admin", authenticated_user["username"])
        self.assertEqual(["authenticated"], authenticated_user["roles"])

    def test_invalid_password_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "Credenciais inválidas"):
            authentication.authenticate_user("admin", "senha-incorreta")

    def test_refresh_token_is_rotated_and_old_token_is_revoked(self) -> None:
        authenticated_user = authentication.authenticate_user("admin", "senha-de-teste")
        _, refresh_token = authentication.issue_tokens(authenticated_user)

        refresh_user = authentication.consume_refresh_token(refresh_token)
        self.assertEqual("admin", refresh_user["username"])

        with self.assertRaisesRegex(Exception, "Refresh token inválido"):
            authentication.consume_refresh_token(refresh_token)

    def test_login_rate_limit_blocks_excessive_attempts(self) -> None:
        previous_rate_limit = authentication.LOGIN_RATE_LIMIT
        authentication.LOGIN_RATE_LIMIT = 1
        try:
            authentication.enforce_login_rate_limit("username:admin")
            with self.assertRaisesRegex(Exception, "Muitas tentativas"):
                authentication.enforce_login_rate_limit("username:admin")
        finally:
            authentication.LOGIN_RATE_LIMIT = previous_rate_limit

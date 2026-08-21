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


class AuthenticationTestCase(unittest.TestCase):
    def test_valid_username_and_password_are_authenticated(self) -> None:
        authenticated_user = authentication.authenticate_user("admin", "senha-de-teste")

        self.assertEqual("admin", authenticated_user["username"])
        self.assertEqual(["authenticated"], authenticated_user["roles"])

    def test_invalid_password_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "Credenciais inválidas"):
            authentication.authenticate_user("admin", "senha-incorreta")

    def test_refresh_token_is_valid_and_unique(self) -> None:
        authenticated_user = authentication.authenticate_user("admin", "senha-de-teste")
        _, first_refresh_token = authentication.issue_tokens(authenticated_user)
        _, second_refresh_token = authentication.issue_tokens(authenticated_user)

        self.assertNotEqual(first_refresh_token, second_refresh_token)

        refresh_user = authentication.consume_refresh_token(first_refresh_token)
        self.assertEqual("admin", refresh_user["username"])
        self.assertEqual(["authenticated"], refresh_user["roles"])

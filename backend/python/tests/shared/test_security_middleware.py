import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.presentation.middleware.security import (
    create_request_size_limit_middleware,
    create_security_headers_middleware,
)


class SecurityMiddlewareIntegrationTestCase(unittest.TestCase):
    def test_request_body_limit_is_preserved(self) -> None:
        app = FastAPI()
        app.middleware("http")(create_request_size_limit_middleware(1024))

        @app.post("/test")
        async def test_endpoint() -> dict[str, bool]:
            return {"ok": True}

        client = TestClient(app)
        response = client.post(
            "/test",
            content=b"x",
            headers={"Content-Length": "1025"},
        )

        self.assertEqual(413, response.status_code)
        self.assertEqual(
            {"detail": "Corpo da requisição muito grande."},
            response.json(),
        )

    def test_security_headers_are_preserved_in_production(self) -> None:
        app = FastAPI()
        app.middleware("http")(create_security_headers_middleware("production"))

        @app.get("/test")
        async def test_endpoint() -> dict[str, bool]:
            return {"ok": True}

        response = TestClient(app).get("/test")

        self.assertEqual("nosniff", response.headers["x-content-type-options"])
        self.assertEqual("DENY", response.headers["x-frame-options"])
        self.assertEqual("no-referrer", response.headers["referrer-policy"])
        self.assertEqual(
            "camera=(), microphone=(), geolocation=()",
            response.headers["permissions-policy"],
        )
        self.assertEqual(
            "max-age=31536000; includeSubDomains",
            response.headers["strict-transport-security"],
        )

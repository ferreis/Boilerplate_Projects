from fastapi import Request
from fastapi.responses import JSONResponse


def create_request_size_limit_middleware(max_request_body_bytes: int):
    async def request_size_limit_middleware(request: Request, call_next):
        content_length = request.headers.get("Content-Length")
        if (
            content_length
            and content_length.isdigit()
            and int(content_length) > max_request_body_bytes
        ):
            return JSONResponse(
                status_code=413,
                content={"detail": "Corpo da requisição muito grande."},
            )
        return await call_next(request)

    return request_size_limit_middleware


def create_security_headers_middleware(app_env: str):
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if app_env == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return security_headers_middleware

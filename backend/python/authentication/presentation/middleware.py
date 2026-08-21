from fastapi import Request
from fastapi.responses import JSONResponse

from authentication.application.interfaces.authentication_ports import TokenService
from authentication.domain.exceptions import ExpiredTokenError, InvalidTokenError


def create_jwt_middleware(token_service: TokenService):
    async def jwt_middleware(request: Request, call_next):
        authorization_header = request.headers.get("Authorization", "").strip()

        if not authorization_header:
            return await call_next(request)

        authorization_parts = authorization_header.split(" ", 1)
        if len(authorization_parts) != 2 or authorization_parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token inválido."},
            )

        access_token = authorization_parts[1].strip()
        if not access_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token ausente."},
            )

        try:
            request.state.user = token_service.decode_access_token(access_token)
        except RuntimeError:
            return JSONResponse(
                status_code=503,
                content={"detail": "Autenticação não está configurada."},
            )
        except ExpiredTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token expirado."},
            )
        except InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Access token inválido."},
            )

        return await call_next(request)

    return jwt_middleware

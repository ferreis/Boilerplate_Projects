import os

import redis
from fastapi import HTTPException, Request


redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


def get_current_user(request: Request) -> dict:
    authenticated_user = getattr(request.state, "user", None)
    if not isinstance(authenticated_user, dict):
        raise HTTPException(status_code=401, detail="Autenticação obrigatória.")
    return authenticated_user


def require_roles(*allowed_roles: str):
    normalized_allowed_roles = {role.strip() for role in allowed_roles if role.strip()}

    def validate_user_role(request: Request) -> dict:
        authenticated_user = get_current_user(request)
        user_roles = authenticated_user.get("roles", [])
        normalized_user_roles = {
            str(role).strip() for role in user_roles if str(role).strip()
        }

        if not normalized_allowed_roles.intersection(normalized_user_roles):
            raise HTTPException(status_code=403, detail="Permissão insuficiente.")

        return authenticated_user

    return validate_user_role

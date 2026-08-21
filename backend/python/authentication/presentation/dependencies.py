from fastapi import HTTPException, Request

from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.policies.role_policy import has_any_role


def get_current_user(request: Request) -> AuthenticatedUser:
    authenticated_user = getattr(request.state, "user", None)
    if not isinstance(authenticated_user, AuthenticatedUser):
        raise HTTPException(status_code=401, detail="Autenticação obrigatória.")
    return authenticated_user


def require_roles(*allowed_roles: str):
    def validate_user_role(request: Request) -> AuthenticatedUser:
        authenticated_user = get_current_user(request)
        if not has_any_role(authenticated_user.roles, allowed_roles):
            raise HTTPException(status_code=403, detail="Permissão insuficiente.")
        return authenticated_user

    return validate_user_role

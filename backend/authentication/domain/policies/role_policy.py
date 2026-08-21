from collections.abc import Iterable


def has_any_role(user_roles: Iterable[str], allowed_roles: Iterable[str]) -> bool:
    normalized_user_roles = {
        str(role).strip() for role in user_roles if str(role).strip()
    }
    normalized_allowed_roles = {
        str(role).strip() for role in allowed_roles if str(role).strip()
    }
    return bool(normalized_user_roles.intersection(normalized_allowed_roles))

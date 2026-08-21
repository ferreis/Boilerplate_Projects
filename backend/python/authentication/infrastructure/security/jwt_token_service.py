import uuid
from datetime import datetime, timedelta, timezone

import jwt

from authentication.application.dto.session import SessionTokens
from authentication.domain.entities.authenticated_user import AuthenticatedUser
from authentication.domain.exceptions import ExpiredTokenError, InvalidTokenError
from shared.infrastructure.config.settings import AuthenticationSettings


class JwtTokenService:
    def __init__(self, settings: AuthenticationSettings) -> None:
        self._settings = settings

    def issue_session(self, user: AuthenticatedUser) -> SessionTokens:
        access_token = self._create_token(
            user=user,
            expires_delta=timedelta(minutes=self._settings.access_token_expire_minutes),
            token_type="access",
        )
        refresh_token = self._create_token(
            user=user,
            expires_delta=timedelta(days=self._settings.refresh_token_expire_days),
            token_type="refresh",
            refresh_identifier=str(uuid.uuid4()),
        )
        return SessionTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_in_seconds=self._settings.access_token_expire_minutes * 60,
        )

    def decode_access_token(self, access_token: str) -> AuthenticatedUser:
        return self._decode_token(access_token, "access")

    def decode_refresh_token(self, refresh_token: str) -> AuthenticatedUser:
        return self._decode_token(refresh_token, "refresh", require_refresh_identifier=True)

    def _create_token(
        self,
        user: AuthenticatedUser,
        expires_delta: timedelta,
        token_type: str,
        refresh_identifier: str | None = None,
    ) -> str:
        payload: dict[str, object] = {
            "sub": user.username,
            "username": user.username,
            "roles": list(user.roles),
            "exp": datetime.now(timezone.utc) + expires_delta,
            "iss": self._settings.jwt_issuer,
            "token_type": token_type,
        }
        if refresh_identifier:
            payload["jti"] = refresh_identifier

        return jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def _decode_token(
        self,
        token: str,
        expected_token_type: str,
        require_refresh_identifier: bool = False,
    ) -> AuthenticatedUser:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
                issuer=self._settings.jwt_issuer,
            )
        except jwt.ExpiredSignatureError as error:
            raise ExpiredTokenError from error
        except jwt.InvalidTokenError as error:
            raise InvalidTokenError from error

        if payload.get("token_type") != expected_token_type:
            raise InvalidTokenError

        if require_refresh_identifier:
            refresh_identifier = str(payload.get("jti") or "").strip()
            try:
                uuid.UUID(refresh_identifier)
            except ValueError as error:
                raise InvalidTokenError from error

        roles = payload.get("roles", [])
        if not isinstance(roles, (list, tuple)):
            raise InvalidTokenError

        subject = payload.get("sub")
        return AuthenticatedUser(
            username=str(payload.get("username") or "").strip(),
            roles=tuple(str(role) for role in roles),
            subject=str(subject) if subject is not None else None,
        )

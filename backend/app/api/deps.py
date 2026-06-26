"""Shared FastAPI dependencies: current user and role-based access control."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

import jwt
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import CastCoreError, ErrorCode
from app.core.security import API_TOKEN_PREFIX, decode_token
from app.db.session import get_db
from app.models.user import User
from app.services import auth_service

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbDep,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=401)
    token = authorization.split(" ", 1)[1]

    # Personal access tokens (prefixed) authenticate as their owner.
    if token.startswith(API_TOKEN_PREFIX):
        user = await auth_service.authenticate_api_token(db, token)
        if user is None:
            raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=401)
        return user

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise CastCoreError(ErrorCode.AUTH_TOKEN_EXPIRED, http_status=401) from exc
    except jwt.PyJWTError as exc:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=401) from exc

    if payload.get("type") != "access":
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=401)

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError) as exc:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=401) from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=403)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_session_id(
    authorization: Annotated[str | None, Header()] = None,
) -> uuid.UUID | None:
    """Best-effort session id (``sid``) from the access token; None for API tokens."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    if token.startswith(API_TOKEN_PREFIX):
        return None
    try:
        sid = decode_token(token).get("sid")
        return uuid.UUID(str(sid)) if sid else None
    except (jwt.PyJWTError, ValueError, TypeError):
        return None


CurrentSessionId = Annotated["uuid.UUID | None", Depends(get_current_session_id)]


def require_roles(*roles: str) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Dependency factory: allow access only to users holding one of ``roles``.

    Admin always passes. Usage::

        @router.get(..., dependencies=[Depends(require_roles("operator"))])
    """

    async def _checker(user: CurrentUser) -> User:
        names = set(user.role_names)
        if "admin" in names or names.intersection(roles):
            return user
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=403)

    return _checker

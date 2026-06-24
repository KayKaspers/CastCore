"""Authentication & user-provisioning logic (DB-facing)."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import Role, Session, User


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    res = await db.execute(select(User).where(User.username == username))
    return res.scalar_one_or_none()


async def get_roles_by_name(db: AsyncSession, names: list[str]) -> list[Role]:
    res = await db.execute(select(Role).where(Role.name.in_(names)))
    return list(res.scalars().all())


async def create_user(
    db: AsyncSession,
    *,
    username: str,
    password: str,
    email: str | None,
    language: str,
    role_names: list[str],
) -> User:
    roles = await get_roles_by_name(db, role_names)
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        language=language,
        roles=roles,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate(db: AsyncSession, username: str, password: str) -> User:
    user = await get_user_by_username(db, username)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise CastCoreError(ErrorCode.AUTH_INVALID_CREDENTIALS, http_status=401)
    user.last_login_at = dt.datetime.now(dt.timezone.utc)
    return user


async def issue_token_pair(
    db: AsyncSession, user: User, *, user_agent: str | None = None, ip: str | None = None
) -> tuple[str, str]:
    """Create an access JWT and a persisted, hashed refresh token."""
    settings = get_settings()
    refresh = generate_refresh_token()
    session = Session(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh),
        user_agent=user_agent,
        ip=ip,
        expires_at=dt.datetime.now(dt.timezone.utc)
        + dt.timedelta(days=settings.refresh_token_ttl_days),
    )
    db.add(session)
    await db.flush()
    access = create_access_token(str(user.id), extra={"roles": user.role_names})
    return access, refresh


async def rotate_refresh_token(
    db: AsyncSession, refresh_token: str
) -> tuple[str, str, User]:
    """Validate a refresh token, revoke it, and issue a fresh pair (rotation)."""
    token_hash = hash_token(refresh_token)
    res = await db.execute(select(Session).where(Session.refresh_token_hash == token_hash))
    session = res.scalar_one_or_none()
    now = dt.datetime.now(dt.timezone.utc)
    if session is None or session.revoked_at is not None or session.expires_at < now:
        raise CastCoreError(ErrorCode.AUTH_TOKEN_EXPIRED, http_status=401)

    session.revoked_at = now
    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise CastCoreError(ErrorCode.AUTH_FORBIDDEN, http_status=403)
    access, refresh = await issue_token_pair(db, user, user_agent=session.user_agent, ip=session.ip)
    return access, refresh, user


async def revoke_all_sessions(db: AsyncSession, user_id: uuid.UUID) -> None:
    res = await db.execute(
        select(Session).where(Session.user_id == user_id, Session.revoked_at.is_(None))
    )
    now = dt.datetime.now(dt.timezone.utc)
    for session in res.scalars().all():
        session.revoked_at = now

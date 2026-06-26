"""User-management endpoints (admin only)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate, user_to_out
from app.services import audit_service, auth_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.get("", response_model=list[UserOut])
async def list_users(db: DbDep) -> list[UserOut]:
    res = await db.execute(select(User).order_by(User.created_at))
    return [user_to_out(u) for u in res.scalars().all()]


@router.post("", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: DbDep, actor: CurrentUser) -> UserOut:
    if await auth_service.get_user_by_username(db, payload.username):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"username": "taken"}, http_status=409)
    user = await auth_service.create_user(
        db,
        username=payload.username,
        password=payload.password,
        email=payload.email,
        language=payload.language,
        role_names=payload.roles,
    )
    await audit_service.record(db, actor_id=actor.id, action="user.create", target_type="user",
                               target_id=str(user.id), meta={"username": user.username})
    return user_to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: uuid.UUID, payload: UserUpdate, db: DbDep) -> UserOut:
    user = await db.get(User, user_id)
    if user is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"user_id": "not_found"}, http_status=404)
    if payload.email is not None:
        user.email = payload.email
    if payload.language is not None:
        user.language = payload.language
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    if payload.roles is not None:
        user.roles = await auth_service.get_roles_by_name(db, payload.roles)
    await db.flush()
    return user_to_out(user)


@router.post("/{user_id}/2fa/reset", response_model=UserOut)
async def reset_2fa(user_id: uuid.UUID, db: DbDep, actor: CurrentUser) -> UserOut:
    """Clear a user's 2FA (recovery for a lost second factor)."""
    user = await db.get(User, user_id)
    if user is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"user_id": "not_found"}, http_status=404)
    user.totp_enabled = False
    user.totp_secret = None
    await db.flush()
    await audit_service.record(db, actor_id=actor.id, action="user.2fa_reset", target_type="user",
                               target_id=str(user.id), meta={"username": user.username})
    return user_to_out(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, db: DbDep, actor: CurrentUser) -> None:
    user = await db.get(User, user_id)
    if user is not None:
        await audit_service.record(db, actor_id=actor.id, action="user.delete", target_type="user",
                                   target_id=str(user_id), meta={"username": user.username})
        await db.delete(user)

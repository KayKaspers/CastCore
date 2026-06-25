"""Settings endpoints: per-user profile (incl. persisted language) and instance settings."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import CurrentUser, DbDep, require_roles
from app.schemas.user import UserOut, user_to_out
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


class ProfileUpdate(BaseModel):
    language: str | None = Field(default=None, pattern="^(de|en)$")
    email: EmailStr | None = None


class GlobalSettingsUpdate(BaseModel):
    instance_name: str | None = Field(default=None, max_length=128)
    default_language: str | None = Field(default=None, pattern="^(de|en)$")


@router.get("/me", response_model=UserOut)
async def get_profile(user: CurrentUser) -> UserOut:
    return user_to_out(user)


@router.patch("/me", response_model=UserOut)
async def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbDep) -> UserOut:
    if payload.language is not None:
        user.language = payload.language
    if payload.email is not None:
        user.email = payload.email
    await db.flush()
    return user_to_out(user)


@router.get("", dependencies=[Depends(require_roles("admin"))])
async def get_global_settings(db: DbDep) -> dict:
    return await settings_service.get_global(db)


@router.patch("", dependencies=[Depends(require_roles("admin"))])
async def update_global_settings(payload: GlobalSettingsUpdate, db: DbDep) -> dict:
    for key, value in payload.model_dump(exclude_none=True).items():
        await settings_service.set_global(db, key, value)
    return await settings_service.get_global(db)

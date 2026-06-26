"""Linked platform accounts — list, refresh, disconnect."""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.core.errors import CastCoreError, ErrorCode
from app.models.platform_account import PlatformAccount
from app.schemas.platform_account import PlatformAccountOut, account_to_out
from app.services import audit_service, oauth_service

router = APIRouter(prefix="/platform-accounts", tags=["platform-accounts"])


@router.get("", response_model=list[PlatformAccountOut])
async def list_accounts(user: CurrentUser, db: DbDep) -> list[PlatformAccountOut]:
    res = await db.execute(select(PlatformAccount).order_by(PlatformAccount.created_at))
    return [account_to_out(a) for a in res.scalars().all()]


@router.post("/{account_id}/refresh", response_model=PlatformAccountOut)
async def refresh_account(account_id: uuid.UUID, user: CurrentUser, db: DbDep) -> PlatformAccountOut:
    account = await db.get(PlatformAccount, account_id)
    if account is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"account_id": "not_found"}, http_status=404)
    await oauth_service.refresh_account(db, account)
    await audit_service.record(db, actor_id=user.id, action="platform.token_refresh",
                               target_type="platform_account", target_id=str(account.id))
    return account_to_out(account)


@router.delete("/{account_id}", status_code=204)
async def disconnect_account(account_id: uuid.UUID, user: CurrentUser, db: DbDep) -> None:
    account = await db.get(PlatformAccount, account_id)
    if account is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"account_id": "not_found"}, http_status=404)
    await audit_service.record(db, actor_id=user.id, action="platform.disconnect",
                               target_type="platform_account", target_id=str(account.id),
                               meta={"provider": account.provider})
    await db.delete(account)

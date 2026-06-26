"""Personal access tokens — each user manages their own programmatic API tokens."""

from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbDep
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import generate_api_token, hash_token
from app.models.user import ApiToken
from app.schemas.token import ApiTokenCreate, ApiTokenCreated, ApiTokenOut
from app.services import audit_service

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.get("", response_model=list[ApiTokenOut])
async def list_tokens(user: CurrentUser, db: DbDep) -> list[ApiTokenOut]:
    res = await db.execute(
        select(ApiToken).where(ApiToken.user_id == user.id).order_by(ApiToken.created_at)
    )
    return [ApiTokenOut.model_validate(t) for t in res.scalars().all()]


@router.post("", response_model=ApiTokenCreated, status_code=201)
async def create_token(payload: ApiTokenCreate, user: CurrentUser, db: DbDep) -> ApiTokenCreated:
    raw = generate_api_token()
    expires_at = None
    if payload.expires_in_days is not None:
        expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=payload.expires_in_days)
    token = ApiToken(
        user_id=user.id,
        name=payload.name,
        token_hash=hash_token(raw),
        expires_at=expires_at,
    )
    db.add(token)
    await db.flush()
    await audit_service.record(db, actor_id=user.id, action="token.create", target_type="api_token",
                               target_id=str(token.id), meta={"name": token.name})
    return ApiTokenCreated(token=raw, **ApiTokenOut.model_validate(token).model_dump())


@router.delete("/{token_id}", status_code=204)
async def revoke_token(token_id: uuid.UUID, user: CurrentUser, db: DbDep) -> None:
    token = await db.get(ApiToken, token_id)
    if token is None or token.user_id != user.id:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"token_id": "not_found"}, http_status=404)
    await audit_service.record(db, actor_id=user.id, action="token.revoke", target_type="api_token",
                               target_id=str(token.id), meta={"name": token.name})
    await db.delete(token)

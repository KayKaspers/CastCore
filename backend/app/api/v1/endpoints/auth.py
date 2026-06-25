"""Authentication endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, Request

from app.api.deps import CurrentUser, DbDep
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, TokenPair
from app.schemas.user import UserOut, user_to_out
from app.services import audit_service, auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: DbDep,
    request: Request,
    user_agent: Annotated[str | None, Header()] = None,
) -> LoginResponse:
    user = await auth_service.authenticate(db, payload.username, payload.password)
    ip = request.client.host if request.client else None
    access, refresh = await auth_service.issue_token_pair(db, user, user_agent=user_agent, ip=ip)
    await audit_service.record(db, actor_id=user.id, action="auth.login", ip=ip)
    return LoginResponse(access_token=access, refresh_token=refresh, user=user_to_out(user))


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: DbDep) -> TokenPair:
    access, refresh_token, _ = await auth_service.rotate_refresh_token(db, payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh_token)


@router.post("/logout", status_code=204)
async def logout(user: CurrentUser, db: DbDep) -> None:
    await auth_service.revoke_all_sessions(db, user.id)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return user_to_out(user)

"""Authentication endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbDep
from app.core import totp
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import decrypt_secret, encrypt_secret
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, TokenPair
from app.schemas.user import UserOut, user_to_out
from app.services import audit_service, auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class TotpSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class TotpCodeRequest(BaseModel):
    code: str = Field(min_length=1)


class TotpStatusResponse(BaseModel):
    enabled: bool


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: DbDep,
    request: Request,
    user_agent: Annotated[str | None, Header()] = None,
) -> LoginResponse:
    user = await auth_service.authenticate(
        db, payload.username, payload.password, totp_code=payload.totp_code
    )
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


@router.post("/2fa/setup", response_model=TotpSetupResponse)
async def totp_setup(user: CurrentUser, db: DbDep) -> TotpSetupResponse:
    """Generate a fresh TOTP secret (stored encrypted, not yet active)."""
    secret = totp.generate_secret()
    user.totp_secret = encrypt_secret(secret)
    user.totp_enabled = False
    await db.flush()
    return TotpSetupResponse(
        secret=secret,
        otpauth_uri=totp.provisioning_uri(secret, account=user.username),
    )


@router.post("/2fa/verify", response_model=TotpStatusResponse)
async def totp_verify(payload: TotpCodeRequest, user: CurrentUser, db: DbDep) -> TotpStatusResponse:
    """Confirm a code from the authenticator app and activate 2FA."""
    if not user.totp_secret:
        raise CastCoreError(ErrorCode.AUTH_TOTP_REQUIRED, http_status=400)
    if not totp.verify(decrypt_secret(user.totp_secret), payload.code):
        raise CastCoreError(ErrorCode.AUTH_TOTP_INVALID, http_status=400)
    user.totp_enabled = True
    await db.flush()
    await audit_service.record(db, actor_id=user.id, action="auth.2fa_enabled")
    return TotpStatusResponse(enabled=True)


@router.post("/2fa/disable", response_model=TotpStatusResponse)
async def totp_disable(payload: TotpCodeRequest, user: CurrentUser, db: DbDep) -> TotpStatusResponse:
    """Disable 2FA — requires a valid current code to prevent lock-in mistakes."""
    if not user.totp_enabled or not user.totp_secret:
        return TotpStatusResponse(enabled=False)
    if not totp.verify(decrypt_secret(user.totp_secret), payload.code):
        raise CastCoreError(ErrorCode.AUTH_TOTP_INVALID, http_status=400)
    user.totp_enabled = False
    user.totp_secret = None
    await db.flush()
    await audit_service.record(db, actor_id=user.id, action="auth.2fa_disabled")
    return TotpStatusResponse(enabled=False)

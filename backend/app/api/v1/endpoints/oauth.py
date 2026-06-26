"""Platform OAuth flow: authorize-URL minting and the provider callback."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, DbDep
from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode
from app.schemas.platform_account import AuthorizeUrlOut, ProviderInfo
from app.services import audit_service, oauth_service

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(user: CurrentUser) -> list[ProviderInfo]:
    return [ProviderInfo(provider=p, enabled=oauth_service.is_enabled(p)) for p in oauth_service.PROVIDERS]


@router.post("/{provider}/authorize", response_model=AuthorizeUrlOut)
async def authorize(provider: str, user: CurrentUser) -> AuthorizeUrlOut:
    if provider not in oauth_service.PROVIDERS:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "unknown"}, http_status=404)
    if not oauth_service.is_enabled(provider):
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"provider": "disabled"}, http_status=400)
    state = oauth_service.build_state(user.id, provider)
    return AuthorizeUrlOut(authorize_url=oauth_service.build_authorize_url(provider, state))


@router.get("/{provider}/callback", include_in_schema=False)
async def callback(provider: str, db: DbDep, code: str | None = None, state: str | None = None):
    """Provider redirect target. Exchanges the code, links the account, returns to the UI."""
    base = get_settings().public_base_url.rstrip("/")
    fail = RedirectResponse(url=f"{base}/resources?error=oauth", status_code=303)
    if not code or not state or provider not in oauth_service.PROVIDERS:
        return fail
    try:
        user_id = oauth_service.verify_state(state, provider)
        account = await oauth_service.exchange_code(db, provider, code, user_id)
        await audit_service.record(db, actor_id=user_id, action="platform.connect",
                                   target_type="platform_account", target_id=str(account.id),
                                   meta={"provider": provider})
    except CastCoreError:
        return fail
    except Exception:  # noqa: BLE001 - provider/network failure must not 500 the browser
        return fail
    return RedirectResponse(url=f"{base}/resources?connected={provider}", status_code=303)

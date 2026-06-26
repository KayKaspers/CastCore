"""Setup-wizard endpoints.

Admin bootstrap (`/setup/admin`) is unauthenticated but only works while no user
exists. Once setup is complete, mutating setup endpoints require an admin.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.core.ratelimit import rate_limit
from app.schemas.setup import AdminCreate, SetupStatus, SystemCheckResult
from app.schemas.user import UserOut, user_to_out
from app.services import setup_service

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/state", response_model=SetupStatus)
async def state(db: DbDep) -> SetupStatus:
    return await setup_service.get_status(db)


@router.post("/admin", response_model=UserOut, status_code=201, dependencies=[Depends(rate_limit("setup_admin"))])
async def create_admin(payload: AdminCreate, db: DbDep) -> UserOut:
    user = await setup_service.create_admin(db, payload)
    return user_to_out(user)


@router.post("/syscheck", response_model=SystemCheckResult)
async def syscheck() -> SystemCheckResult:
    return await setup_service.run_syscheck()


@router.post("/step/{step}", response_model=SetupStatus, dependencies=[Depends(require_roles("admin"))])
async def set_step(step: str, db: DbDep, status: str = "done") -> SetupStatus:
    return await setup_service.set_step(db, step, status)


@router.post("/complete", response_model=SetupStatus, dependencies=[Depends(require_roles("admin"))])
async def complete(db: DbDep) -> SetupStatus:
    if await setup_service.is_setup_complete(db):
        raise CastCoreError(ErrorCode.SETUP_ALREADY_COMPLETED, http_status=409)
    return await setup_service.set_step(db, "complete", "done")

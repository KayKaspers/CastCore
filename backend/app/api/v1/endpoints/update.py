"""Update / version endpoint (admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import DbDep, require_roles
from app.services import update_service

router = APIRouter(prefix="/update", tags=["update"], dependencies=[Depends(require_roles("admin"))])


class UpdateState(BaseModel):
    current_version: str
    environment: str
    deployment: str
    db_revision: str | None
    head_revision: str | None
    up_to_date: bool


@router.get("/state", response_model=UpdateState)
async def update_state(db: DbDep) -> UpdateState:
    return UpdateState(**await update_service.get_state(db))

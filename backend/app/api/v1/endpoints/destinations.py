"""Destination CRUD (operator+). Stream keys are encrypted at rest and write-only."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbDep, require_roles
from app.core.errors import CastCoreError, ErrorCode
from app.core.security import encrypt_secret
from app.models.streaming import Destination
from app.schemas.streaming import DestinationIn, DestinationOut, destination_to_out

router = APIRouter(
    prefix="/destinations",
    tags=["streaming"],
    dependencies=[Depends(require_roles("operator"))],
)


@router.get("", response_model=list[DestinationOut])
async def list_destinations(db: DbDep) -> list[DestinationOut]:
    res = await db.execute(select(Destination).order_by(Destination.name))
    return [destination_to_out(d) for d in res.scalars().all()]


@router.post("", response_model=DestinationOut, status_code=201)
async def create_destination(payload: DestinationIn, db: DbDep) -> DestinationOut:
    dest = Destination(
        name=payload.name,
        kind=payload.kind,
        url=payload.url,
        enabled=payload.enabled,
        stream_key=encrypt_secret(payload.stream_key) if payload.stream_key else None,
    )
    db.add(dest)
    await db.flush()
    return destination_to_out(dest)


@router.patch("/{destination_id}", response_model=DestinationOut)
async def update_destination(destination_id: uuid.UUID, payload: DestinationIn, db: DbDep) -> DestinationOut:
    dest = await db.get(Destination, destination_id)
    if dest is None:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"destination": "not_found"}, http_status=404)
    dest.name = payload.name
    dest.kind = payload.kind
    dest.url = payload.url
    dest.enabled = payload.enabled
    # Only replace the stored key when a new one is supplied (write-only semantics).
    if payload.stream_key:
        dest.stream_key = encrypt_secret(payload.stream_key)
    await db.flush()
    return destination_to_out(dest)


@router.delete("/{destination_id}", status_code=204)
async def delete_destination(destination_id: uuid.UUID, db: DbDep) -> None:
    dest = await db.get(Destination, destination_id)
    if dest is not None:
        await db.delete(dest)

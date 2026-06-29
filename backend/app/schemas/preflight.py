"""Preflight 2.0 report schemas. No secrets/stream keys are ever serialized."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class PreflightCheckOut(BaseModel):
    code: str
    category: str
    level: str  # ok | warn | error
    blocking: bool = False
    affected_component: str
    affected_output_id: str | None = None
    docs_url: str
    params: dict = Field(default_factory=dict)


class PreflightReportOut(BaseModel):
    id: uuid.UUID | None = None
    stream_job_id: uuid.UUID
    level: str  # green | yellow | red | gray
    can_start: bool
    created_at: dt.datetime | None = None
    ttl_seconds: int
    stale: bool = False
    started_by_user_id: uuid.UUID | None = None
    checks: list[PreflightCheckOut] = Field(default_factory=list)
    blocking_errors: list[PreflightCheckOut] = Field(default_factory=list)
    warnings: list[PreflightCheckOut] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)

"""Setup-wizard schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

# Canonical ordered wizard steps (kept in sync with frontend setup.step.* i18n keys).
SETUP_STEPS: list[str] = [
    "language",
    "admin",
    "deployment",
    "ffmpeg",
    "ffprobe",
    "dataDir",
    "mediaDir",
    "logDir",
    "storage",
    "syscheck",
    "complete",
]


class StepState(BaseModel):
    step: str
    status: str = "pending"  # pending|done|skipped


class SetupStatus(BaseModel):
    completed: bool
    current_step: str | None
    steps: list[StepState]


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
    language: str = Field(default="de", pattern="^(de|en)$")


class SystemCheckItem(BaseModel):
    key: str
    ok: bool
    detail: str | None = None


class SystemCheckResult(BaseModel):
    level: str  # green|yellow|red
    items: list[SystemCheckItem]

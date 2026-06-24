"""Storage-source schemas. SMB passwords are write-only."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class LocalSourceIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    path: str = Field(min_length=1, max_length=2048)
    read_only: bool = True


class SmbSourceIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    server: str = Field(min_length=1, max_length=255)
    share: str = Field(min_length=1, max_length=255)
    domain: str | None = None
    username: str | None = None
    password: str | None = None  # write-only
    smb_version: str | None = None
    mount_path: str | None = None  # defaults to MOUNT_DIR/<id>
    read_only: bool = True
    automount: bool = False


class SmbOut(BaseModel):
    server: str
    share: str
    domain: str | None
    username: str | None
    smb_version: str | None
    mount_path: str
    has_password: bool


class StorageSourceOut(BaseModel):
    id: uuid.UUID
    name: str
    source_class: str
    type: str
    path: str | None
    effective_path: str | None
    read_only: bool
    automount: bool
    status: str
    last_error: str | None
    last_scan_at: dt.datetime | None
    smb: SmbOut | None = None


class TestResult(BaseModel):
    ok: bool
    detail: str | None = None


class BrowseEntry(BaseModel):
    name: str
    rel_path: str
    abs_path: str
    is_dir: bool
    size: int
    streamable: bool


class BrowseResult(BaseModel):
    base: str
    subpath: str
    entries: list[BrowseEntry]

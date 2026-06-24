"""Schemas for FFmpeg profiles, destinations and stream jobs."""

from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict, Field


# --- FFmpeg profiles ---
class FFmpegProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    global_opts: dict = Field(default_factory=lambda: {"hide_banner": "", "loglevel": "info"})
    video: dict = Field(default_factory=dict)
    audio: dict = Field(default_factory=dict)
    filters: dict = Field(default_factory=dict)
    copy_mode: bool = False
    expert_args: list[str] = Field(default_factory=list)


class FFmpegProfileOut(FFmpegProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


# --- Destinations ---
class DestinationIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    kind: str = Field(default="rtmp", pattern="^(platform|rtmp|hls|recording|preview)$")
    url: str = Field(min_length=1, max_length=1024)
    stream_key: str | None = None  # write-only; encrypted at rest
    enabled: bool = True


class DestinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    kind: str
    url: str
    enabled: bool
    has_stream_key: bool = False


def destination_to_out(dest) -> DestinationOut:
    return DestinationOut(
        id=dest.id,
        name=dest.name,
        kind=dest.kind,
        url=dest.url,
        enabled=dest.enabled,
        has_stream_key=dest.stream_key is not None,
    )


# --- Stream jobs (with nested inputs/outputs) ---
class InputIn(BaseModel):
    kind: str = Field(default="file", pattern="^(file|url|device)$")
    uri: str = Field(min_length=1, max_length=2048)
    options: dict = Field(default_factory=dict)
    loop: bool = False
    reconnect: bool = False
    order: int = 0


class OutputIn(BaseModel):
    destination_id: uuid.UUID | None = None
    format: str = Field(default="flv", pattern="^(flv|hls|mpegts|mp4)$")
    output_opts: dict = Field(default_factory=dict)
    enabled: bool = True


class StreamJobIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    type: str = Field(default="single", pattern="^(single|channel)$")
    autostart: bool = False
    enabled: bool = True
    ffmpeg_profile_id: uuid.UUID | None = None
    fallback_policy: dict = Field(default_factory=dict)
    recording_enabled: bool = False
    recording_retention_days: int = 0
    inputs: list[InputIn] = Field(default_factory=list)
    outputs: list[OutputIn] = Field(default_factory=list)


class OutputStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    output_id: uuid.UUID
    state: str
    fps: float | None = None
    bitrate_kbps: float | None = None
    speed: float | None = None
    reconnect_count: int = 0


class StreamJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    type: str
    status: str
    autostart: bool
    enabled: bool
    ffmpeg_profile_id: uuid.UUID | None
    recording_enabled: bool = False
    created_at: dt.datetime


class CommandPreviewOut(BaseModel):
    previews: dict[str, str]  # output_id -> masked command string


class PreflightCheck(BaseModel):
    key: str
    level: str  # ok | warn | error
    detail: str | None = None


class PreflightReport(BaseModel):
    level: str  # green | yellow | red
    checks: list[PreflightCheck]

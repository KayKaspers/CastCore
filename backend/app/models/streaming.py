"""Streaming models: FFmpeg profiles, stream jobs, inputs, outputs, destinations,
process status."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, uuid_pk


class FFmpegProfile(Base, TimestampMixin):
    __tablename__ = "ffmpeg_profiles"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    global_opts: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    video: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # codec/bitrate/res/fps/preset/...
    audio: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    copy_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expert_args: Mapped[list] = mapped_column(JSON, default=list, nullable=False)


class Destination(Base, TimestampMixin):
    __tablename__ = "destinations"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default="rtmp", nullable=False)  # platform/rtmp/hls/recording/preview
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    stream_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # encrypted at rest
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StreamJob(Base, TimestampMixin):
    __tablename__ = "stream_jobs"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(String(16), default="single", nullable=False)  # single/channel
    status: Mapped[str] = mapped_column(String(16), default="stopped", nullable=False)
    autostart: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ffmpeg_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("ffmpeg_profiles.id", ondelete="SET NULL"), nullable=True
    )
    fallback_policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    profile: Mapped[FFmpegProfile | None] = relationship(lazy="selectin")
    inputs: Mapped[list["Input"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", lazy="selectin", order_by="Input.order"
    )
    outputs: Mapped[list["Output"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )


class Input(Base, TimestampMixin):
    __tablename__ = "inputs"

    id: Mapped[uuid.UUID] = uuid_pk()
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(16), default="file", nullable=False)  # file/url/device
    uri: Mapped[str] = mapped_column(String(2048), nullable=False)
    options: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    loop: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reconnect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    job: Mapped[StreamJob] = relationship(back_populates="inputs")


class Output(Base, TimestampMixin):
    __tablename__ = "outputs"

    id: Mapped[uuid.UUID] = uuid_pk()
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True
    )
    format: Mapped[str] = mapped_column(String(16), default="flv", nullable=False)  # flv/hls/mpegts/mp4
    output_opts: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    job: Mapped[StreamJob] = relationship(back_populates="outputs")
    destination: Mapped[Destination | None] = relationship(lazy="selectin")
    status: Mapped["ProcessStatus | None"] = relationship(
        back_populates="output", cascade="all, delete-orphan", uselist=False, lazy="selectin"
    )


class ProcessStatus(Base, TimestampMixin):
    __tablename__ = "process_status"

    id: Mapped[uuid.UUID] = uuid_pk()
    output_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("outputs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(16), default="stopped", nullable=False)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    bitrate_kbps: Mapped[float | None] = mapped_column(Float, nullable=True)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    dropped_frames: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reconnect_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cpu_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    rss_mb: Mapped[float | None] = mapped_column(Float, nullable=True)

    output: Mapped[Output] = relationship(back_populates="status")

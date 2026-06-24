"""Media library schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class MediaProbeOut(BaseModel):
    container: str | None = None
    duration_s: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None


class MediaItemOut(BaseModel):
    id: uuid.UUID
    storage_source_id: uuid.UUID
    rel_path: str
    filename: str
    kind: str
    size_bytes: int
    streamable: bool
    problem_flags: dict
    probe: MediaProbeOut | None = None


class ScanResult(BaseModel):
    files: int
    indexed: int
    probed: int


def media_to_out(item) -> MediaItemOut:
    probe = None
    if item.probe is not None:
        probe = MediaProbeOut(
            container=item.probe.container, duration_s=item.probe.duration_s,
            video_codec=item.probe.video_codec, audio_codec=item.probe.audio_codec,
            width=item.probe.width, height=item.probe.height, fps=item.probe.fps,
        )
    return MediaItemOut(
        id=item.id, storage_source_id=item.storage_source_id, rel_path=item.rel_path,
        filename=item.filename, kind=item.kind, size_bytes=item.size_bytes,
        streamable=item.streamable, problem_flags=item.problem_flags, probe=probe,
    )

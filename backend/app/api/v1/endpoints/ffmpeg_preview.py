"""Command-preview endpoint: turn a structured FFmpeg profile into a masked preview.

Demonstrates the Command Builder wired to the API. The real Stream Job endpoints
(Phase 1) reuse the same builder to construct argv for the Process Manager.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.errors import CastCoreError
from app.services.ffmpeg import (
    AudioSettings,
    CommandBuildError,
    FFmpegCommand,
    Input,
    Output,
    OutputFormat,
    VideoSettings,
)

router = APIRouter(prefix="/ffmpeg", tags=["ffmpeg"])


class InputIn(BaseModel):
    uri: str
    options: dict[str, str] = Field(default_factory=dict)
    loop: bool = False
    reconnect: bool = False


class VideoIn(BaseModel):
    codec: str = "libx264"
    bitrate: str | None = None
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    preset: str | None = None
    tune: str | None = None
    gop: int | None = None
    pixel_format: str | None = None


class AudioIn(BaseModel):
    codec: str = "aac"
    bitrate: str | None = None
    disabled: bool = False


class OutputIn(BaseModel):
    uri: str
    fmt: OutputFormat
    video: VideoIn | None = None
    audio: AudioIn | None = None
    extra_options: dict[str, str] = Field(default_factory=dict)


class PreviewRequest(BaseModel):
    inputs: list[InputIn]
    outputs: list[OutputIn]
    filter_complex: str | None = None
    expert_args: list[str] = Field(default_factory=list)


class PreviewResponse(BaseModel):
    preview: str  # masked, human-readable
    argv_length: int


@router.post("/preview", response_model=PreviewResponse)
async def preview_command(req: PreviewRequest) -> PreviewResponse:
    cmd = FFmpegCommand(
        inputs=[Input(uri=i.uri, options=i.options, loop=i.loop, reconnect=i.reconnect) for i in req.inputs],
        outputs=[
            Output(
                uri=o.uri,
                fmt=o.fmt,
                video=VideoSettings(**o.video.model_dump()) if o.video else None,
                audio=AudioSettings(**o.audio.model_dump()) if o.audio else None,
                extra_options=o.extra_options,
            )
            for o in req.outputs
        ],
        filter_complex=req.filter_complex,
        expert_args=req.expert_args,
    )
    try:
        argv = cmd.build()
    except CommandBuildError as exc:
        raise CastCoreError(exc.code, params={"detail": str(exc)}) from exc
    return PreviewResponse(preview=cmd.preview(), argv_length=len(argv))

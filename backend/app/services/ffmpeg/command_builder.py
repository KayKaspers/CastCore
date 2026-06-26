"""FFmpeg Command Builder — security-critical core module.

Builds FFmpeg invocations as **argument lists** (never shell strings). The argv is
later handed to ``asyncio.create_subprocess_exec`` (``shell=False``) by the Process
Manager, so there is no shell to inject into.

Guarantees:
- Correct option ordering: global → per-input options → input → filters →
  per-output options → output.
- Every value is validated/whitelisted where it maps to an enum (codec, format, …).
- Multiple inputs and multiple outputs.
- Stream-copy (``-c copy``) vs re-encode, HLS / RTMP / SRT, loop, reconnect, filters.
- A masked preview for the UI (stream keys and credentials in URLs are hidden).

This module has **no side effects**: it only constructs and validates argv. It must
stay fully unit-tested (see tests/ffmpeg/test_command_builder.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class OutputFormat(str, Enum):
    FLV = "flv"  # RTMP
    HLS = "hls"
    MPEGTS = "mpegts"  # SRT / UDP
    MP4 = "mp4"  # recording


# Conservative whitelists. Expert mode appends raw args separately and is clearly
# marked in the UI; these lists guard the structured fields.
VIDEO_CODECS = {
    "copy", "libx264", "libx265", "h264_nvenc", "hevc_nvenc",
    "h264_qsv", "h264_vaapi", "libvpx-vp9", "libaom-av1",
}
AUDIO_CODECS = {"copy", "aac", "libfdk_aac", "libmp3lame", "libopus", "ac3"}
PRESETS = {
    "ultrafast", "superfast", "veryfast", "faster", "fast",
    "medium", "slow", "slower", "veryslow",
}
PIXEL_FORMATS = {"yuv420p", "yuv422p", "yuv444p", "nv12", "p010le"}

# Tokens allowed in a structured argument value. Anything else must go through the
# explicit expert-args channel. This is defence in depth — there is no shell — but it
# keeps malformed/abusive values out of structured fields.
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9 _\-.,:;/=@%+?&()\[\]{}'\"!~|]*$")

# URL secret patterns to mask in previews/logs.
_RTMP_KEY = re.compile(r"(rtmp[s]?://[^\s]+?/)([^/\s?]+)(\?[^\s]*)?$", re.IGNORECASE)
_QUERY_SECRET = re.compile(r"([?&](?:key|streamkey|token|password|auth|sig)=)([^&\s]+)", re.IGNORECASE)


class CommandBuildError(ValueError):
    """Raised on invalid/unsafe command-builder input. Carries a translatable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _check_value(value: str, field_name: str) -> str:
    if not _SAFE_VALUE.match(value):
        raise CommandBuildError(
            "ffmpeg.invalid_parameter",
            f"Unsafe characters in field '{field_name}': {value!r}",
        )
    return value


@dataclass
class Input:
    uri: str  # file path, device, or URL
    options: dict[str, str] = field(default_factory=dict)  # e.g. {"re": "", "f": "lavfi"}
    loop: bool = False
    reconnect: bool = False

    def to_args(self) -> list[str]:
        args: list[str] = []
        if self.loop:
            # -stream_loop -1 loops the input indefinitely (file inputs).
            args += ["-stream_loop", "-1"]
        if self.reconnect:
            args += [
                "-reconnect", "1",
                "-reconnect_streamed", "1",
                "-reconnect_delay_max", "5",
            ]
        for key, val in self.options.items():
            _check_value(key, "input option key")
            args.append(f"-{key}")
            if val != "":
                args.append(_check_value(val, f"input option '{key}'"))
        if not self.uri:
            raise CommandBuildError("ffmpeg.no_input", "Input URI is empty")
        args += ["-i", _check_value(self.uri, "input uri")]
        return args


@dataclass
class VideoSettings:
    codec: str = "libx264"
    bitrate: str | None = None  # e.g. "6000k"
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    preset: str | None = None
    tune: str | None = None
    gop: int | None = None  # keyframe interval (frames)
    pixel_format: str | None = None

    def validate(self) -> None:
        if self.codec not in VIDEO_CODECS:
            raise CommandBuildError("ffmpeg.invalid_parameter", f"Unknown video codec: {self.codec}")
        if self.preset and self.preset not in PRESETS:
            raise CommandBuildError("ffmpeg.invalid_parameter", f"Unknown preset: {self.preset}")
        if self.pixel_format and self.pixel_format not in PIXEL_FORMATS:
            raise CommandBuildError("ffmpeg.invalid_parameter", f"Unknown pixel format: {self.pixel_format}")


@dataclass
class AudioSettings:
    codec: str = "aac"
    bitrate: str | None = None  # e.g. "160k"
    disabled: bool = False

    def validate(self) -> None:
        if self.codec not in AUDIO_CODECS:
            raise CommandBuildError("ffmpeg.invalid_parameter", f"Unknown audio codec: {self.codec}")


@dataclass
class Output:
    uri: str
    fmt: OutputFormat
    video: VideoSettings | None = None
    audio: AudioSettings | None = None
    extra_options: dict[str, str] = field(default_factory=dict)

    def to_args(self) -> list[str]:
        if not self.uri:
            raise CommandBuildError("ffmpeg.no_output", "Output URI is empty")
        args: list[str] = []

        if self.video is None:
            args += ["-vn"]
        elif self.video.codec == "copy":
            args += ["-c:v", "copy"]
        else:
            self.video.validate()
            args += ["-c:v", self.video.codec]
            if self.video.bitrate:
                args += ["-b:v", _check_value(self.video.bitrate, "video bitrate")]
            if self.video.width and self.video.height:
                args += ["-s", f"{int(self.video.width)}x{int(self.video.height)}"]
            if self.video.fps:
                args += ["-r", str(int(self.video.fps))]
            if self.video.preset:
                args += ["-preset", self.video.preset]
            if self.video.tune:
                args += ["-tune", _check_value(self.video.tune, "tune")]
            if self.video.gop:
                args += ["-g", str(int(self.video.gop))]
            if self.video.pixel_format:
                args += ["-pix_fmt", self.video.pixel_format]

        if self.audio is None or self.audio.disabled:
            args += ["-an"]
        elif self.audio.codec == "copy":
            args += ["-c:a", "copy"]
        else:
            self.audio.validate()
            args += ["-c:a", self.audio.codec]
            if self.audio.bitrate:
                args += ["-b:a", _check_value(self.audio.bitrate, "audio bitrate")]

        for key, val in self.extra_options.items():
            _check_value(key, "output option key")
            args.append(f"-{key}")
            if val != "":
                args.append(_check_value(val, f"output option '{key}'"))

        args += ["-f", self.fmt.value, _check_value(self.uri, "output uri")]
        return args


@dataclass
class FFmpegCommand:
    inputs: list[Input] = field(default_factory=list)
    outputs: list[Output] = field(default_factory=list)
    filter_complex: str | None = None
    global_options: dict[str, str] = field(default_factory=lambda: {"hide_banner": "", "loglevel": "info"})
    expert_args: list[str] = field(default_factory=list)  # raw, user-acknowledged
    ffmpeg_path: str = "ffmpeg"

    def build(self) -> list[str]:
        """Return the full argv in the canonical FFmpeg order."""
        if not self.inputs:
            raise CommandBuildError("ffmpeg.no_input", "At least one input is required")
        if not self.outputs:
            raise CommandBuildError("ffmpeg.no_output", "At least one output is required")

        argv: list[str] = [self.ffmpeg_path]

        # 1) Global options
        for key, val in self.global_options.items():
            _check_value(key, "global option key")
            argv.append(f"-{key}")
            if val != "":
                argv.append(_check_value(val, f"global option '{key}'"))

        # 2) Inputs (each: input options then -i input)
        for inp in self.inputs:
            argv += inp.to_args()

        # 3) Filters
        if self.filter_complex:
            argv += ["-filter_complex", _check_value(self.filter_complex, "filter_complex")]

        # 4) Expert args (raw, already acknowledged in the UI). Validated for safe tokens.
        for raw in self.expert_args:
            argv.append(_check_value(raw, "expert arg"))

        # 5) Outputs (each: output options then output)
        for out in self.outputs:
            argv += out.to_args()

        return argv

    def preview(self) -> str:
        """A human-readable, secret-masked command preview for the UI."""
        return mask_command(self.build())


def mask_command(argv: list[str]) -> str:
    """Join argv into a display string with stream keys / URL secrets masked."""
    masked: list[str] = []
    for token in argv:
        t = _QUERY_SECRET.sub(lambda m: f"{m.group(1)}••••", token)
        t = _RTMP_KEY.sub(lambda m: f"{m.group(1)}••••{(m.group(3) or '')}", t)
        masked.append(t if " " not in t else f'"{t}"')
    return " ".join(masked)

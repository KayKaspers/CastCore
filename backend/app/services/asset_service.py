"""Asset handling — secure image uploads.

Security (per the brief):
- Validate by **magic bytes**, not just the file extension.
- Enforce a maximum size.
- Store under a **generated, safe filename** (uuid + ext); the user's original name is
  kept only as metadata, never used on disk.
- No execution; assets are served with a fixed safe content type and as attachments.
"""

from __future__ import annotations

import hashlib
import struct
import uuid
from pathlib import Path

from app.core.config import get_settings
from app.core.errors import CastCoreError, ErrorCode

MAX_BYTES = 10 * 1024 * 1024  # 10 MB

# magic-byte signature -> (mime, extension)
_SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", ("image/png", "png")),
    (b"\xff\xd8\xff", ("image/jpeg", "jpg")),
    (b"GIF87a", ("image/gif", "gif")),
    (b"GIF89a", ("image/gif", "gif")),
]


def _detect(content: bytes) -> tuple[str, str]:
    for sig, out in _SIGNATURES:
        if content.startswith(sig):
            return out
    # WebP: RIFF....WEBP
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ("image/webp", "webp")
    raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"upload": "unsupported_type"})


def _dimensions(content: bytes, mime: str) -> tuple[int | None, int | None]:
    """Best-effort width/height for PNG and JPEG without external deps."""
    try:
        if mime == "image/png" and len(content) >= 24:
            w, h = struct.unpack(">II", content[16:24])
            return int(w), int(h)
        if mime == "image/jpeg":
            i = 2
            n = len(content)
            while i + 9 < n:
                if content[i] != 0xFF:
                    i += 1
                    continue
                marker = content[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3):  # SOF markers
                    h, w = struct.unpack(">HH", content[i + 5:i + 9])
                    return int(w), int(h)
                seg_len = struct.unpack(">H", content[i + 2:i + 4])[0]
                i += 2 + seg_len
    except (struct.error, IndexError):
        pass
    return None, None


def validate_and_store(content: bytes, original_name: str | None) -> dict:
    if not content:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"upload": "empty"})
    if len(content) > MAX_BYTES:
        raise CastCoreError(ErrorCode.VALIDATION_FAILED, params={"upload": "too_large"})

    mime, ext = _detect(content)
    width, height = _dimensions(content, mime)
    sha256 = hashlib.sha256(content).hexdigest()

    settings = get_settings()
    asset_dir = Path(settings.thumbnail_dir) / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{ext}"  # safe, generated; never the user's name
    path = asset_dir / filename
    path.write_bytes(content)

    return {
        "filename": filename,
        "original_name": (original_name or "")[:512] or None,
        "path": str(path),
        "kind": "image",
        "mime": mime,
        "size_bytes": len(content),
        "width": width,
        "height": height,
        "sha256": sha256,
    }

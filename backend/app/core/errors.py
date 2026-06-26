"""Translatable error codes.

The backend never returns baked-in English prose for user-facing errors. It returns a
machine-readable ``code`` (and optional ``params``) that the frontend maps to a
localized DE/EN string via i18next. This keeps the app fully bilingual end to end.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


class CastCoreError(HTTPException):
    """An HTTP error carrying a translatable code instead of a fixed message."""

    def __init__(
        self,
        code: str,
        *,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        params: dict[str, Any] | None = None,
        level: str = "error",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.params = params or {}
        self.level = level
        super().__init__(
            status_code=http_status,
            detail={"error": {"code": code, "params": self.params, "level": level}},
            headers=headers,
        )


# Canonical error codes. Keep in sync with frontend i18n (error.* keys).
class ErrorCode:
    AUTH_INVALID_CREDENTIALS = "auth.invalid_credentials"
    AUTH_TOKEN_EXPIRED = "auth.token_expired"
    AUTH_FORBIDDEN = "auth.forbidden"
    AUTH_TOTP_REQUIRED = "auth.totp_required"
    AUTH_TOTP_INVALID = "auth.totp_invalid"
    AUTH_RATE_LIMITED = "auth.rate_limited"

    SETUP_ALREADY_COMPLETED = "setup.already_completed"
    SETUP_FFMPEG_NOT_FOUND = "setup.ffmpeg_not_found"

    FFMPEG_INVALID_PARAMETER = "ffmpeg.invalid_parameter"
    FFMPEG_NO_INPUT = "ffmpeg.no_input"
    FFMPEG_NO_OUTPUT = "ffmpeg.no_output"

    PREFLIGHT_SOURCE_UNREACHABLE = "preflight.source_unreachable"
    PREFLIGHT_NO_VIDEO = "preflight.no_video"
    PREFLIGHT_MISSING_STREAM_KEY = "preflight.missing_stream_key"

    STORAGE_TEST_FAILED = "storage.test_failed"
    STORAGE_MOUNT_FAILED = "storage.mount_failed"

    VALIDATION_FAILED = "validation.failed"

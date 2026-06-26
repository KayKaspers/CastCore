"""Shared types for platform metadata-push adapters."""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from app.core.errors import ErrorCode


@dataclass
class FieldRef:
    """A translatable code + params for a per-field warning or the overall error."""

    code: str
    params: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"code": self.code, "params": self.params}


@dataclass
class PushOutcome:
    """Result of a metadata push: which fields were applied, plus warnings / a hard error.

    Adapters never raise for *expected* platform conditions — they record them here so the
    caller can return a uniform, translatable structure. Tokens are never stored on this.
    """

    applied: list[str] = field(default_factory=list)
    warnings: list[FieldRef] = field(default_factory=list)
    error: FieldRef | None = None

    @property
    def status(self) -> str:
        if self.error is not None:
            return "error"
        return "warning" if self.warnings else "success"

    def fail(self, code: str, **params) -> "PushOutcome":
        self.error = FieldRef(code, params)
        return self

    def warn(self, code: str, **params) -> None:
        self.warnings.append(FieldRef(code, params))


def map_http_error(status_code: int, *, provider: str) -> FieldRef:
    """Map a platform HTTP status to a translatable FieldRef."""
    if status_code in (401, 403):
        return FieldRef(ErrorCode.PLATFORM_MISSING_SCOPE, {"provider": provider})
    return FieldRef(ErrorCode.PLATFORM_API_ERROR, {"provider": provider, "status": status_code})


class PlatformAdapter:
    """Base class. Subclasses set ``provider`` and implement ``push``."""

    provider: str = ""

    async def push(
        self,
        http: httpx.AsyncClient,
        access_token: str,
        client_id: str,
        meta: dict,
        *,
        thumbnail: tuple[bytes, str] | None = None,
    ) -> PushOutcome:  # pragma: no cover - interface
        raise NotImplementedError

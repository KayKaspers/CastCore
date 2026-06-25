"""TOTP (RFC 6238) helpers using only the standard library.

The shared secret is generated here, stored **encrypted** on the user, and used to
verify 6-digit codes from an authenticator app (Google Authenticator, Aegis, …).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

_STEP = 30
_DIGITS = 6


def generate_secret() -> str:
    """Return a base32 secret (no padding) suitable for authenticator apps."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _hotp(secret_b32: str, counter: int) -> str:
    pad = "=" * ((8 - len(secret_b32) % 8) % 8)
    key = base64.b32decode(secret_b32 + pad, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{code % (10 ** _DIGITS):0{_DIGITS}d}"


def now_code(secret_b32: str, at: float | None = None) -> str:
    return _hotp(secret_b32, int((at if at is not None else time.time()) // _STEP))


def verify(secret_b32: str | None, code: str | None, window: int = 1) -> bool:
    """Verify a code allowing a ±window step skew."""
    if not secret_b32 or not code:
        return False
    code = code.strip().replace(" ", "")
    if not code.isdigit():
        return False
    counter = int(time.time() // _STEP)
    return any(hmac.compare_digest(_hotp(secret_b32, counter + w), code)
               for w in range(-window, window + 1))


def provisioning_uri(secret_b32: str, account: str, issuer: str = "CastCore") -> str:
    return (
        f"otpauth://totp/{quote(issuer)}:{quote(account)}"
        f"?secret={secret_b32}&issuer={quote(issuer)}&digits={_DIGITS}&period={_STEP}"
    )

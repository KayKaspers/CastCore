"""Security primitives: password hashing, secret encryption, JWT, masking.

- Passwords: argon2id.
- Secrets at rest (stream keys, SMB/OAuth credentials): Fernet symmetric encryption
  using ENCRYPTION_KEY from the environment. The key is never stored in the DB or repo.
- Tokens: short-lived JWT access + rotating refresh (refresh persisted hashed elsewhere).
"""

from __future__ import annotations

import datetime as dt
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def _fernet() -> Fernet:
    key = get_settings().encryption_key
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is not configured; cannot handle secrets.")
    return Fernet(key.encode())


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret for storage. Returns an opaque token string."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:  # pragma: no cover - defensive
        raise RuntimeError("Failed to decrypt secret (wrong ENCRYPTION_KEY?)") from exc


def mask_secret(value: str | None, *, visible: int = 4) -> str:
    """Mask a secret for display: keep the last ``visible`` chars."""
    if not value:
        return ""
    if len(value) <= visible:
        return "•" * len(value)
    return "•" * (len(value) - visible) + value[-visible:]


def create_access_token(subject: str, *, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = dt.datetime.now(dt.timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": now + dt.timedelta(minutes=settings.access_token_ttl_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])

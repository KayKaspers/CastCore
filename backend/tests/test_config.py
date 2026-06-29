"""Tests for the fail-closed production secret validation in Settings (SEC-01).

Pure unit tests: they construct ``Settings`` directly with explicit kwargs (init args take
precedence over env/.env), so they need no database, no Redis and no ffmpeg.
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from pydantic import ValidationError

from app.core.config import Settings

_STRONG_SECRET = "a" * 64  # length >= 32, no insecure marker
_STRONG_DB_PW = "S0me-Str0ng-Db-Passw0rd"


def _valid_encryption_key() -> str:
    return Fernet.generate_key().decode()


def test_production_rejects_insecure_defaults():
    with pytest.raises(ValidationError) as exc:
        Settings(
            castcore_env="production",
            secret_key="changeme",
            encryption_key="",
            postgres_password="castcore",
        )
    msg = str(exc.value)
    assert "SECRET_KEY" in msg
    assert "ENCRYPTION_KEY" in msg
    assert "POSTGRES_PASSWORD" in msg
    # The error must not leak secret values, only variable names.
    assert "changeme" not in msg


def test_production_rejects_invalid_fernet_key():
    with pytest.raises(ValidationError) as exc:
        Settings(
            castcore_env="production",
            secret_key=_STRONG_SECRET,
            encryption_key="not-a-valid-fernet-key",
            postgres_password=_STRONG_DB_PW,
        )
    assert "ENCRYPTION_KEY" in str(exc.value)


def test_production_rejects_short_secret_key():
    with pytest.raises(ValidationError) as exc:
        Settings(
            castcore_env="production",
            secret_key="tooshort",
            encryption_key=_valid_encryption_key(),
            postgres_password=_STRONG_DB_PW,
        )
    assert "SECRET_KEY" in str(exc.value)


def test_production_accepts_strong_values():
    s = Settings(
        castcore_env="production",
        secret_key=_STRONG_SECRET,
        encryption_key=_valid_encryption_key(),
        postgres_password=_STRONG_DB_PW,
    )
    assert s.is_production


def test_development_allows_insecure_defaults():
    # Local dev / CI convenience must stay usable with the built-in defaults.
    s = Settings(
        castcore_env="development",
        secret_key="changeme",
        encryption_key="",
        postgres_password="castcore",
    )
    assert not s.is_production

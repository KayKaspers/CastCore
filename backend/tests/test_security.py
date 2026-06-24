"""Tests for security primitives (hashing, encryption, JWT, masking)."""

from __future__ import annotations

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_token,
    decrypt_secret,
    encrypt_secret,
    generate_refresh_token,
    hash_password,
    hash_token,
    mask_secret,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"
    assert verify_password("correct horse battery staple", h)
    assert not verify_password("wrong", h)


def test_secret_encryption_roundtrip():
    token = encrypt_secret("live_streamkey_123")
    assert token != "live_streamkey_123"
    assert decrypt_secret(token) == "live_streamkey_123"


def test_mask_secret_keeps_tail():
    assert mask_secret("abcd1234") == "••••1234"
    assert mask_secret("ab") == "••"
    assert mask_secret(None) == ""


def test_access_token_roundtrip_and_claims():
    token = create_access_token("user-id-1", extra={"roles": ["admin"]})
    payload = decode_token(token)
    assert payload["sub"] == "user-id-1"
    assert payload["type"] == "access"
    assert payload["roles"] == ["admin"]


def test_refresh_token_hash_is_deterministic_and_opaque():
    rt = generate_refresh_token()
    assert len(rt) > 40
    assert hash_token(rt) == hash_token(rt)
    assert hash_token(rt) != rt


def test_tampered_token_rejected():
    token = create_access_token("user-id-1")
    with pytest.raises(jwt.PyJWTError):
        decode_token(token + "tamper")

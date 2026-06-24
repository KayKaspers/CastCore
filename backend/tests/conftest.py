"""Test configuration: set required secrets before settings are first read."""

from __future__ import annotations

import os

from cryptography.fernet import Fernet

os.environ.setdefault("CASTCORE_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())

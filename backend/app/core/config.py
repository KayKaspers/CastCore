"""Application configuration, loaded from environment (see .env.example)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Marker shared by the config default and the .env.example placeholders. Any security-critical
# value still containing it is treated as "not configured" in production.
_INSECURE_MARKER = "changeme"
# Weak built-in defaults that must never be used in production.
_INSECURE_DB_PASSWORDS = {"", "castcore"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # General
    castcore_env: str = Field(default="production")
    default_language: str = Field(default="de")
    tz: str = Field(default="Europe/Berlin")

    # Security
    secret_key: str = Field(default="changeme")
    encryption_key: str = Field(default="")  # Fernet key; required in production
    access_token_ttl_minutes: int = Field(default=30)
    refresh_token_ttl_days: int = Field(default=14)

    # Rate limiting for sensitive auth endpoints (Redis-backed, fixed window).
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_auth_attempts: int = Field(default=10)
    rate_limit_auth_window_seconds: int = Field(default=300)

    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "castcore"
    postgres_user: str = "castcore"
    postgres_password: str = "castcore"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""

    # Paths
    data_dir: Path = Path("/data")
    media_dir: Path = Path("/data/media")
    recordings_dir: Path = Path("/data/recordings")
    log_dir: Path = Path("/data/logs")
    backup_dir: Path = Path("/data/backups")
    mount_dir: Path = Path("/data/mounts")
    thumbnail_dir: Path = Path("/data/thumbnails")

    # FFmpeg
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    ffprobe_path: str = "/usr/bin/ffprobe"

    # Preflight (gate before stream start)
    preflight_required_before_start: bool = Field(default=False)
    preflight_block_on_red: bool = Field(default=False)
    preflight_report_ttl_seconds: int = Field(default=600)

    # Safe media processing (mitigation for FFmpeg decoder CVEs, e.g. CVE-2026-8461/MagicYUV).
    # When enabled, media from untrusted sources is treated cautiously and risky codecs are
    # flagged/blocked instead of being decoded automatically.
    safe_media_processing_enabled: bool = Field(default=True)
    media_autothumbnails_enabled: bool = Field(default=True)
    block_risky_codecs: bool = Field(default=True)
    # Comma-separated extra codecs to treat as risky (merged with the built-in defaults).
    risky_codecs_blocklist: str = Field(default="magicyuv")

    # MediaMTX (optional media router; compose profile "mediamtx")
    mediamtx_enabled: bool = Field(default=False)
    mediamtx_api_url: str = Field(default="http://mediamtx:9997")
    # Base URL CastCore/FFmpeg uses to pull an ingest path back in as a source.
    mediamtx_rtsp_url: str = Field(default="rtsp://mediamtx:8554")

    # Public base URL of this instance (scheme + host, no trailing slash), e.g.
    # https://stream.example.com — used to build OAuth redirect URIs. Required for OAuth.
    public_base_url: str = Field(default="")

    # Platform OAuth client credentials (empty disables the provider).
    youtube_client_id: str = Field(default="")
    youtube_client_secret: str = Field(default="")
    twitch_client_id: str = Field(default="")
    twitch_client_secret: str = Field(default="")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/0"

    @property
    def is_production(self) -> bool:
        return self.castcore_env == "production"

    @model_validator(mode="after")
    def _enforce_production_secrets(self) -> Settings:
        """Fail closed: refuse to start in production with insecure secret defaults.

        Development/test (``CASTCORE_ENV != production``) keep the convenient defaults so
        local work and the test suite stay usable. Error messages name the offending
        environment variable and the fix, but never echo any secret value.
        """
        if not self.is_production:
            return self

        problems: list[str] = []

        secret = self.secret_key.strip()
        if not secret or _INSECURE_MARKER in secret.lower():
            problems.append("SECRET_KEY is unset or still the insecure default")
        elif len(secret) < 32:
            problems.append(
                "SECRET_KEY is too short (use >= 32 chars, e.g. `openssl rand -hex 32`)"
            )

        enc = self.encryption_key.strip()
        if not enc or _INSECURE_MARKER in enc.lower():
            problems.append("ENCRYPTION_KEY is unset or still the insecure default")
        else:
            try:
                Fernet(enc.encode())
            except Exception:  # noqa: BLE001 - any failure means the key is unusable
                problems.append(
                    "ENCRYPTION_KEY is not a valid Fernet key "
                    '(generate: python -c "from cryptography.fernet import Fernet; '
                    'print(Fernet.generate_key().decode())")'
                )

        if self.postgres_password in _INSECURE_DB_PASSWORDS or (
            _INSECURE_MARKER in self.postgres_password.lower()
        ):
            problems.append("POSTGRES_PASSWORD is unset or still the insecure default")

        if problems:
            raise ValueError(
                "Refusing to start in production (CASTCORE_ENV=production) with insecure "
                "configuration. Fix these environment variables (see .env.example) and "
                "restart:\n  - " + "\n  - ".join(problems)
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

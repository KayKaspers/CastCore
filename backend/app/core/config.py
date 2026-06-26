"""Application configuration, loaded from environment (see .env.example)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()

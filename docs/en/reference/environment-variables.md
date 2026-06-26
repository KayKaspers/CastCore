---
title: "Environment variables"
description: "Reference of all `.env` variables."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Environment variables

> Configuration is done via the `.env` file (template: `.env.example`).

**Audience:** administrators. See also [Configuration](/docs/en/reference/configuration.md).

## General

| Variable | Description | Example |
| --- | --- | --- |
| `CASTCORE_ENV` | `production` or `development` | `production` |
| `DOMAIN` | public hostname (reverse proxy) | `castcore.example.com` |
| `TZ` | timezone | `Europe/Berlin` |
| `DEFAULT_LANGUAGE` | default language `de`/`en` | `de` |

## Security (must change)

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | signing key for JWT (64 hex chars) |
| `ENCRYPTION_KEY` | Fernet key for encrypted secrets – **keep it safe** |
| `ACCESS_TOKEN_TTL_MINUTES` | access-token lifetime (default 30) |
| `REFRESH_TOKEN_TTL_DAYS` | refresh-token lifetime (default 14) |

## Database & Redis

| Variable | Description |
| --- | --- |
| `POSTGRES_HOST` / `_PORT` / `_DB` / `_USER` / `_PASSWORD` | PostgreSQL connection |
| `REDIS_HOST` / `_PORT` / `_PASSWORD` | Redis connection |

## Paths

| Variable | Default |
| --- | --- |
| `DATA_DIR` | `/data` |
| `MEDIA_DIR` | `/data/media` |
| `RECORDINGS_DIR` | `/data/recordings` |
| `LOG_DIR` | `/data/logs` |
| `BACKUP_DIR` | `/data/backups` |
| `MOUNT_DIR` | `/data/mounts` |
| `THUMBNAIL_DIR` | `/data/thumbnails` |

## FFmpeg & proxy

| Variable | Description |
| --- | --- |
| `FFMPEG_PATH` / `FFPROBE_PATH` | paths to FFmpeg/ffprobe |
| `ACME_EMAIL` | email for automatic HTTPS certificates (Caddy) |
| `MEDIAMTX_ENABLED` / `MEDIAMTX_API_URL` / `MEDIAMTX_RTSP_URL` | optional MediaMTX integration (enable, API address, RTSP pull base) |
| `PUBLIC_BASE_URL` | public URL of the instance (for OAuth redirects); e.g. `https://stream.example.com` |
| `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` | YouTube OAuth (empty = disabled) |
| `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` | Twitch OAuth (empty = disabled) |

## Notes

> 🔐 Never commit real values – `.env` is git-ignored. Generate secrets:
> `openssl rand -hex 32` (SECRET_KEY), `openssl rand -base64 32 | tr '+/' '-_'` (Fernet).

## Related pages

- [Secrets management](/docs/en/admin-guide/secrets.md)
- [Configuration](/docs/en/reference/configuration.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

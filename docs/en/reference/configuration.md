---
title: "Configuration"
description: "All configuration options at a glance."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Configuration

> Overview of **where** CastCore is configured.

**Audience:** administrators.

## Layers

| Layer | What | Where |
| --- | --- | --- |
| **Environment** | secrets, DB/Redis, paths, domain, FFmpeg paths | `.env` (Docker) or `/etc/castcore/castcore.env` (native) |
| **Instance** | instance name, default language | UI → Settings (admin) |
| **Per user** | language | UI → Settings |
| **Domain data** | profiles, destinations, sources, channels, notifications, scheduler | UI / API |

## Environment variables

Full reference: [Environment variables](/docs/en/reference/environment-variables.md).
Important: `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_*`, `REDIS_*`, `DOMAIN`, `DATA_DIR`,
`FFMPEG_PATH`/`FFPROBE_PATH`.

## Instance & user settings

See [Settings](/docs/en/user-guide/settings.md).

## Notes

> 🔐 Secrets belong in the environment, **not** in the repo. `.env` is git-ignored.

## Related pages

- [Environment variables](/docs/en/reference/environment-variables.md) · [Secrets](/docs/en/admin-guide/secrets.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

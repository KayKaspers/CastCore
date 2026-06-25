---
title: "Deployment"
description: "Overview of deployment paths and operating models."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Deployment

> CastCore supports two paths: **Docker-first** (recommended) and **native install**. Both
> bring or install every required component.

**Audience:** administrators. Target systems: Debian 12, Ubuntu Server LTS, LXC, VM, bare
metal, Proxmox.

## Components

| Service | Purpose |
| --- | --- |
| **frontend** | Built React SPA (Nginx). |
| **backend** | FastAPI API + background loops (status consumer, scheduler). |
| **process-manager** | Supervises the long-running FFmpeg processes. |
| **worker** | Short async jobs (scan, ffprobe, thumbnails, backups). |
| **postgres** | Database. |
| **redis** | Cache, queue, control bus (`castcore:control`/`:status`). |
| **caddy** | Reverse proxy + automatic HTTPS. |
| *(optional)* **mediamtx** | Internal media router (compose profile). |

## Paths

- **[Docker Compose](/docs/en/admin-guide/docker-compose.md)** – one command, all services,
  automatic migrations. See [Install with Docker](/docs/en/getting-started/installation-docker.md).
- **Native** – `scripts/install.sh` (systemd services, local DB/Redis). See
  [Native installation](/docs/en/getting-started/installation-native.md).

## Operations topics

- [Reverse proxy](/docs/en/admin-guide/reverse-proxy.md) · [HTTPS](/docs/en/admin-guide/https.md)
- [Storage mounts](/docs/en/admin-guide/storage-mounts.md) · [Secrets](/docs/en/admin-guide/secrets.md)
- [Logs](/docs/en/admin-guide/logs.md) · [Backup & restore](/docs/en/user-guide/backup-restore.md)
- [Updates](/docs/en/user-guide/updates.md)

## Notes

> 🔐 Before going to production: set unique `SECRET_KEY`/`ENCRYPTION_KEY`, enable HTTPS,
> test backups. See [Security best practices](/docs/en/admin-guide/security.md).

## Related pages

- [System requirements](/docs/en/admin-guide/system-requirements.md)
- [Architecture](/docs/en/developer-guide/architecture.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

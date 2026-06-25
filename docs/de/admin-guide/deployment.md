---
title: "Deployment"
description: "Überblick über die Deployment-Wege und Betriebsmodelle."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Deployment

> CastCore unterstützt zwei Wege: **Docker-first** (empfohlen) und **native Installation**.
> Beide bringen alle nötigen Komponenten mit bzw. installieren sie.

**Zielgruppe:** Administratoren. Zielsysteme: Debian 12, Ubuntu Server LTS, LXC, VM,
Bare Metal, Proxmox.

## Komponenten

| Dienst | Zweck |
| --- | --- |
| **frontend** | Ausgeliefertes React-SPA (Nginx). |
| **backend** | FastAPI-API + Hintergrund-Loops (Status-Consumer, Scheduler). |
| **process-manager** | Supervidiert die langlaufenden FFmpeg-Prozesse. |
| **worker** | Kurze Async-Jobs (Scan, ffprobe, Thumbnails, Backups). |
| **postgres** | Datenbank. |
| **redis** | Cache, Queue, Steuerkanal (`castcore:control`/`:status`). |
| **caddy** | Reverse Proxy + automatisches HTTPS. |
| *(optional)* **mediamtx** | Interner Media-Router (Compose-Profil). |

## Wege

- **[Docker Compose](/docs/de/admin-guide/docker-compose.md)** – ein Befehl, alle Dienste,
  Migrationen automatisch. Siehe [Installation mit Docker](/docs/de/getting-started/installation-docker.md).
- **Native** – `scripts/install.sh` (systemd-Dienste, lokale DB/Redis). Siehe
  [Native Installation](/docs/de/getting-started/installation-native.md).

## Betriebsthemen

- [Reverse Proxy](/docs/de/admin-guide/reverse-proxy.md) · [HTTPS](/docs/de/admin-guide/https.md)
- [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md) · [Secrets](/docs/de/admin-guide/secrets.md)
- [Logs](/docs/de/admin-guide/logs.md) · [Backup & Restore](/docs/de/user-guide/backup-restore.md)
- [Updates](/docs/de/user-guide/updates.md)

## Hinweise

> 🔐 Vor dem Produktivbetrieb: eindeutige `SECRET_KEY`/`ENCRYPTION_KEY` setzen, HTTPS
> aktivieren, Backups testen. Siehe [Security Best Practices](/docs/de/admin-guide/security.md).

## Verwandte Seiten

- [Systemanforderungen](/docs/de/admin-guide/system-requirements.md)
- [Architektur](/docs/de/developer-guide/architecture.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Troubleshooting (Admin)"
description: "Einstieg in die Fehlersuche für Administratoren."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Troubleshooting (Admin)

> Einstieg für betriebsnahe Probleme. Die symptombasierte Übersicht steht unter
> [Troubleshooting](/docs/de/troubleshooting/index.md).

**Zielgruppe:** Administratoren.

## Erste Schritte

1. **Status & Logs:**
   ```bash
   docker compose ps
   docker compose logs -f backend process-manager
   ```
2. **Migrationsstatus** prüfen (Updates-Seite / `/api/v1/update/state`).
3. **Health:** `GET /api/v1/system/health` (FFmpeg/ffprobe vorhanden?).

## Häufige Bereiche

| Thema | Seite |
| --- | --- |
| Container/DB/Redis | [Docker-Probleme](/docs/de/troubleshooting/docker.md) |
| Native Installation | [Native Installation](/docs/de/troubleshooting/native-installation.md) |
| HTTPS/Proxy | [HTTPS](/docs/de/admin-guide/https.md) · [Reverse Proxy](/docs/de/admin-guide/reverse-proxy.md) |
| SMB/Storage | [SMB-Probleme](/docs/de/troubleshooting/smb-problems.md) |
| Performance | [Performance](/docs/de/troubleshooting/performance.md) |
| Backup/Restore | [Backup & Restore](/docs/de/user-guide/backup-restore.md) |

## Verwandte Seiten

- [Logs](/docs/de/admin-guide/logs.md) · [Monitoring](/docs/de/user-guide/monitoring.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Troubleshooting (admin)"
description: "Entry point to troubleshooting for administrators."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Troubleshooting (admin)

> Entry point for operational problems. The symptom-based overview is at
> [Troubleshooting](/docs/en/troubleshooting/index.md).

**Audience:** administrators.

## First steps

1. **Status & logs:**
   ```bash
   docker compose ps
   docker compose logs -f backend process-manager
   ```
2. Check the **migration status** (Updates page / `/api/v1/update/state`).
3. **Health:** `GET /api/v1/system/health` (FFmpeg/ffprobe present?).

## Common areas

| Topic | Page |
| --- | --- |
| Containers/DB/Redis | [Docker problems](/docs/en/troubleshooting/docker.md) |
| Native installation | [Native installation](/docs/en/troubleshooting/native-installation.md) |
| HTTPS/proxy | [HTTPS](/docs/en/admin-guide/https.md) · [Reverse proxy](/docs/en/admin-guide/reverse-proxy.md) |
| SMB/storage | [SMB problems](/docs/en/troubleshooting/smb-problems.md) |
| Performance | [Performance](/docs/en/troubleshooting/performance.md) |
| Backup/restore | [Backup & restore](/docs/en/user-guide/backup-restore.md) |

## Related pages

- [Logs](/docs/en/admin-guide/logs.md) · [Monitoring](/docs/en/user-guide/monitoring.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

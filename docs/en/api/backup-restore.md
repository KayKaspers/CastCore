---
title: "API: backup/restore"
description: "Create, download and restore backups."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: backup/restore

> Logical backups (gz-JSON) of the application tables. **Admin** required.

**Audience:** developers / integrators.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/backups` | List backups |
| `POST` | `/api/v1/backups` | Create a backup |
| `GET` | `/api/v1/backups/{id}/download` | Backup file (`.json.gz`) |
| `POST` | `/api/v1/backups/{id}/restore?confirm=true` | Restore (overwrites everything) |
| `DELETE` | `/api/v1/backups/{id}` | Delete a backup |

## Important

> ⚠️ **Restore without `confirm=true` → 400.** Restore **overwrites all data** (except the
> backup history and the audit log).

> 🔐 Secrets are stored in the backup only **encrypted** – restore requires the same
> `ENCRYPTION_KEY` ([Secrets](/docs/en/admin-guide/secrets.md)).

## Update status

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/update/state` | Version, deployment, migration status |

## Audit

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/audit` | Audit events (filter `action`, pagination) |

## Related pages

- [Backup & restore (UI)](/docs/en/user-guide/backup-restore.md) · [Updates](/docs/en/user-guide/updates.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

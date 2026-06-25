---
title: "Updates"
description: "Update CastCore (Docker and native)."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Updates

> The **Updates** page (`/updates`, admin only) shows the running version, the deployment
> mode and the database **migration status**.

**Audience:** administrators.

## What the page shows

| Field | Meaning |
| --- | --- |
| **Version** | Running CastCore version. |
| **Environment** | `production` / `development`. |
| **Deployment** | `docker` or `native` (auto-detected). |
| **DB revision / head revision** | Current vs. latest Alembic migration. |
| **Schema up to date** | Whether the database is at the latest revision. |

## Updating with Docker

```bash
git pull
docker compose pull        # if using prebuilt images
docker compose up -d --build
```

The backend runs **migrations automatically** on start
([Install with Docker](/docs/en/getting-started/installation-docker.md)).

## Native update

```bash
sudo ./scripts/update.sh
```

`update.sh` creates a backup **before** updating, syncs the code, applies migrations and
restarts the services.

## Before every update

> ⚠️ **Backup recommended.** Create a [backup](/docs/en/user-guide/backup-restore.md)
> first. If something goes wrong, the rollback is restoring the pre-update backup.

## Notes

> 💡 If it says "migrations: pending", they are applied automatically on the next Docker
> start; natively via `update.sh`.

## Related pages

- [Backup & restore](/docs/en/user-guide/backup-restore.md)
- [Install with Docker](/docs/en/getting-started/installation-docker.md)
- [Migrations (developer)](/docs/en/developer-guide/migrations.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

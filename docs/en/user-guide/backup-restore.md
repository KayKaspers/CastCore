---
title: "Backup & restore"
description: "Back up and restore the database and configuration."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Backup & restore

> CastCore creates **logical backups** (gz-JSON) of all application tables. Admin only.

**Audience:** administrators. UI area: **Backup / restore** (`/backup`).

## Create a backup

**Create backup** → a gz-JSON artifact in the backup directory. It contains the database
and configuration; **secrets stay encrypted**.

## Download / delete

Use **↓** to download a backup, **✕** to delete it.

## Restore

**Restore** overwrites **all** current data (with confirmation). Excluded are the **backup
history** and the **[audit log](/docs/en/admin-guide/security.md)**.

> ⚠️ Before an update/restore, a fresh backup is always worth it.

> 🔐 **Without the matching `ENCRYPTION_KEY`, the contained secrets are unusable.** Keep
> the key safe and separate ([Secrets](/docs/en/admin-guide/secrets.md)).

## Scheduled backups

Via the [scheduler](/docs/en/user-guide/settings.md) you can create backups on a schedule
(`backup` action). Successful backups raise the `backup_done` event.

## Related pages

- [Updates](/docs/en/user-guide/updates.md) · [API: backup/restore](/docs/en/api/backup-restore.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

---
title: "API: Backup/Restore"
description: "Backups erstellen, herunterladen, wiederherstellen."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Backup/Restore

> Logische Backups (gz-JSON) der Anwendungstabellen. **Admin** erforderlich.

**Zielgruppe:** Entwickler / Integratoren.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/backups` | Backups auflisten |
| `POST` | `/api/v1/backups` | Backup erstellen |
| `GET` | `/api/v1/backups/{id}/download` | Backup-Datei (`.json.gz`) |
| `POST` | `/api/v1/backups/{id}/restore?confirm=true` | Wiederherstellen (überschreibt alles) |
| `DELETE` | `/api/v1/backups/{id}` | Backup löschen |

## Wichtig

> ⚠️ **Restore ohne `confirm=true` → 400.** Die Wiederherstellung **überschreibt alle
> Daten** (außer der Backup-Historie und dem Audit-Log).

> 🔐 Secrets liegen im Backup nur **verschlüsselt** vor – Restore benötigt denselben
> `ENCRYPTION_KEY` ([Secrets](/docs/de/admin-guide/secrets.md)).

## Update-Status

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/update/state` | Version, Deployment, Migrationsstatus |

## Audit

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/audit` | Audit-Events (Filter `action`, Paginierung) |

## Verwandte Seiten

- [Backup & Restore (UI)](/docs/de/user-guide/backup-restore.md) · [Updates](/docs/de/user-guide/updates.md)

---
_Stand: 2026-06-24 · Status: Stabil_

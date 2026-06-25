---
title: "Backup & Restore"
description: "Datenbank und Konfiguration sichern und wiederherstellen."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Backup & Restore

> CastCore erstellt **logische Backups** (gz-JSON) aller Anwendungstabellen. Nur Admin.

**Zielgruppe:** Administratoren. UI-Bereich: **Backup / Restore** (`/backup`).

## Backup erstellen

**Backup erstellen** → ein gz-JSON-Artefakt im Backup-Verzeichnis. Es enthält Datenbank
und Konfiguration; **Secrets bleiben verschlüsselt**.

## Herunterladen / Löschen

Über **↓** lädst du ein Backup herunter, über **✕** löschst du es.

## Wiederherstellen

**Wiederherstellen** überschreibt **alle** aktuellen Daten (mit Bestätigung).
Ausgenommen sind die **Backup-Historie** und das **[Audit-Log](/docs/de/admin-guide/security.md)**.

> ⚠️ Vor einem Update/Restore lohnt immer ein frisches Backup.

> 🔐 **Ohne den passenden `ENCRYPTION_KEY` sind die enthaltenen Secrets unbrauchbar.**
> Bewahre den Schlüssel sicher und getrennt auf ([Secrets](/docs/de/admin-guide/secrets.md)).

## Geplante Backups

Über den [Scheduler](/docs/de/user-guide/settings.md) lassen sich Backups zeitgesteuert
erstellen (`backup`-Aktion). Erfolgreiche Backups lösen das Event `backup_done` aus.

## Verwandte Seiten

- [Updates](/docs/de/user-guide/updates.md) · [API: Backup/Restore](/docs/de/api/backup-restore.md)

---
_Stand: 2026-06-24 · Status: Stabil_

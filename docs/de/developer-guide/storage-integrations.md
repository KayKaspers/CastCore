---
title: "Storage-Integrationen"
description: "Quellen-/Mount-Schicht und Erweiterung."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Storage-Integrationen

> Aufbau der Quellen-/Mount-Schicht und wie man neue Quellentypen ergänzt.

**Zielgruppe:** Entwickler.

## Modell

- `storage_sources` ist die **polymorphe Wurzel** (`class`/`type`, Status, Pfad).
- Typ-Detail in eigenen Tabellen, z. B. `smb_sources` (Server/Share/Creds/Mount-Pfad).
- Logik in `app/services/storage_service.py`.

## Sicherheit

- Secrets (SMB-Passwort) **verschlüsselt**; Mount-Credentials in `0600`-Dateien.
- Externe Befehle (`mount.cifs`, `umount`) als **Argumentliste** (kein Shell).
- `browse` ist **traversal-geschützt** (auf den effektiven Pfad beschränkt).

## Einen Quellentyp ergänzen

1. Detail-Tabelle + Migration anlegen, am `storage_sources`-Typ andocken.
2. In `storage_service` `effective_path`, `test_source`, ggf. `mount`/`unmount` erweitern.
3. Endpoints/Schemas und UI ([Quellen](/docs/de/user-guide/sources-storage.md)) ergänzen.
4. Doku (DE+EN) + Manifest aktualisieren.

## Hinweis

Container-Mounts brauchen erweiterte Rechte – bevorzugt
[Host-Mounts](/docs/de/admin-guide/storage-mounts.md).

## Verwandte Seiten

- [API: Quellen](/docs/de/api/sources.md) · [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md)

---
_Stand: 2026-06-24 · Status: Stabil_

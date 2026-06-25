---
title: "Cloud-Quellen"
description: "S3/WebDAV/rclone-Remotes als Quelle vorbereiten."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Cloud-Quellen

> Cloud-Speicher (S3, WebDAV, Nextcloud, B2, R2, Google Drive, Dropbox, OneDrive) als
> Quelle.

**Zielgruppe:** Administratoren.

> ℹ️ **Status:** Die Cloud-Anbindung ist modular **vorbereitet**, aber noch nicht in der
> UI implementiert. Bis dahin lassen sich Cloud-Remotes über **rclone mount** auf dem Host
> einbinden und als [lokale Quelle](/docs/de/user-guide/sources-storage.md) nutzen.

## Übergangslösung: rclone-Mount (Host)

```bash
rclone mount myremote:bucket /mnt/castcore-cloud \
  --vfs-cache-mode full --read-only --daemon
```
Anschließend `/mnt/castcore-cloud` als **lokale Quelle** in CastCore anlegen.

## Geplante Anbindung

Verbindung testen · OAuth/API-Zugangsdaten **verschlüsselt** speichern · Remote
durchsuchen · Cache-Verzeichnis · Sync- oder Mount-Modus · Robustheit bei instabilen
Verbindungen/großen Dateien.

## Hinweise

> 💡 Cloud-Verbindungen sind potenziell instabil – `--vfs-cache-mode full` und großzügige
> Puffer helfen bei großen Mediendateien.

## Verwandte Seiten

- [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md) · [Quellen / Storage](/docs/de/user-guide/sources-storage.md)

---
_Stand: 2026-06-24 · Status: Stabil (Feature in Vorbereitung)_

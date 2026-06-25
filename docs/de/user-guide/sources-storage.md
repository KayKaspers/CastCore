---
title: "Quellen / Storage"
description: "Lokale und Netzwerk-Quellen (SMB) anlegen, testen, mounten, durchsuchen."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Quellen / Storage

> Quellen liefern die Medien für Streams und Channels: lokale Ordner und SMB-Freigaben.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Quellen / Storage** (`/sources`).

## Lokale Quelle anlegen

Name + Pfad (z. B. `/data/media`). Beim Anlegen wird die Erreichbarkeit geprüft
(Status **online/error**).

## SMB-Quelle anlegen

Name, Server/IP, Freigabe, optional Domain/Benutzer/Passwort. **Verbindung testen** prüft
TCP 445. Details/Mount-Thematik: [SMB / CIFS](/docs/de/admin-guide/smb-cifs.md).

## Aktionen

| Aktion | Wirkung |
| --- | --- |
| **Test** | Erreichbarkeit prüfen (Status aktualisieren) |
| **mount / unmount** | SMB ein-/aushängen (Rechte nötig, siehe unten) |
| **Durchsuchen** | Verzeichnis browsen; **„copy path"** kopiert den absoluten Pfad |
| **✕** | Quelle löschen |

## Von der Quelle zum Stream

1. **Durchsuchen** → bei einer Datei **„copy path"**.
2. Pfad im [Stream-Editor](/docs/de/user-guide/stream-editor.md) als Input-URI einfügen,
   oder die Quelle in der [Medienbibliothek](/docs/de/user-guide/media-library.md) scannen.

## Hinweise

> 🔐 SMB-Passwörter werden verschlüsselt gespeichert; das Browsen ist
> **traversal-geschützt** (auf den Quellpfad beschränkt).

> ⚠️ Container-Mounts brauchen erweiterte Rechte – bevorzugt
> [auf dem Host mounten](/docs/de/admin-guide/storage-mounts.md).

## Bei Problemen

[SMB-Probleme](/docs/de/troubleshooting/smb-problems.md)

## Verwandte Seiten

- [Medienbibliothek](/docs/de/user-guide/media-library.md) · [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md)

---
_Stand: 2026-06-24 · Status: Stabil_

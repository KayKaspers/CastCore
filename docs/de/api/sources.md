---
title: "API: Quellen"
description: "Storage-Quellen, Test, Mount, Browse."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Quellen

> Lokale und SMB-Quellen verwalten. Operator+. Passwörter write-only/verschlüsselt.

**Zielgruppe:** Entwickler / Integratoren.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/storage-sources` | Quellen auflisten |
| `POST` | `/api/v1/storage-sources/local` | Lokale Quelle anlegen |
| `POST` | `/api/v1/storage-sources/smb` | SMB-Quelle anlegen |
| `GET/DELETE` | `/api/v1/storage-sources/{id}` | Detail / löschen |
| `POST` | `/api/v1/storage-sources/{id}/test` | Erreichbarkeit testen |
| `POST` | `/api/v1/storage-sources/{id}/mount` · `/unmount` | SMB mounten/aushängen |
| `GET` | `/api/v1/storage-sources/{id}/browse?subpath=` | Verzeichnis durchsuchen |

## Hinweise

- `browse` ist **traversal-geschützt** (auf den Quellpfad beschränkt) und markiert
  streamfähige Medien.
- SMB-Mounts im Container brauchen erweiterte Rechte – siehe
  [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md).
- Fehlgeschlagener `test` löst das Event `source_offline` aus
  ([Benachrichtigungen](/docs/de/user-guide/settings.md)).

## Verwandte Seiten

- [Quellen / Storage (UI)](/docs/de/user-guide/sources-storage.md)
- [Medienbibliothek](/docs/de/api/media-library.md)

---
_Stand: 2026-06-24 · Status: Stabil_

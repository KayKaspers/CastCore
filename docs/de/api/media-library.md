---
title: "API: Medienbibliothek"
description: "Scan, Auflistung, ffprobe-Daten."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Medienbibliothek

> Quellen scannen und indexierte Medien abfragen. Operator+.

**Zielgruppe:** Entwickler / Integratoren.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/api/v1/media/scan/{source_id}` | Quelle scannen (inkrementell) |
| `GET` | `/api/v1/media` | Auflisten/filtern |
| `GET` | `/api/v1/media/{id}` | Detail inkl. ffprobe-Daten |
| `DELETE` | `/api/v1/media/{id}` | Eintrag entfernen |

## Filter (Query)

| Parameter | Bedeutung |
| --- | --- |
| `source_id` | nur Medien dieser Quelle |
| `kind` | `video` / `audio` / `image` / `other` |
| `streamable` | nur streamfähige (`true`) |
| `q` | Suche im Dateinamen |
| `limit` / `offset` | Paginierung |

## Scan-Ergebnis

```json
{ "files": 128, "indexed": 12, "probed": 12 }
```

## Playlists

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/playlists[/{id}]` | Playlists |
| `POST/DELETE` | `/api/v1/playlists/{id}/items[/{item}]` | Items hinzufügen/entfernen |
| `POST` | `/api/v1/playlists/{id}/reorder` | Reihenfolge setzen |
| `GET` | `/api/v1/playlists/{id}/resolve` | Auflösen → absolute Pfade + Dauer |

## Verwandte Seiten

- [Medienbibliothek (UI)](/docs/de/user-guide/media-library.md) · [Playlists](/docs/de/user-guide/playlists.md)

---
_Stand: 2026-06-24 · Status: Stabil_

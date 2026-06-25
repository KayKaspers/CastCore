---
title: "API: media library"
description: "Scan, listing, ffprobe data."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: media library

> Scan sources and query indexed media. Operator+.

**Audience:** developers / integrators.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/media/scan/{source_id}` | Scan a source (incremental) |
| `GET` | `/api/v1/media` | List/filter |
| `GET` | `/api/v1/media/{id}` | Detail incl. ffprobe data |
| `DELETE` | `/api/v1/media/{id}` | Remove an entry |

## Filters (query)

| Parameter | Meaning |
| --- | --- |
| `source_id` | only media of this source |
| `kind` | `video` / `audio` / `image` / `other` |
| `streamable` | only streamable (`true`) |
| `q` | search in the filename |
| `limit` / `offset` | pagination |

## Scan result

```json
{ "files": 128, "indexed": 12, "probed": 12 }
```

## Playlists

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/playlists[/{id}]` | Playlists |
| `POST/DELETE` | `/api/v1/playlists/{id}/items[/{item}]` | Add/remove items |
| `POST` | `/api/v1/playlists/{id}/reorder` | Set order |
| `GET` | `/api/v1/playlists/{id}/resolve` | Resolve → absolute paths + duration |

## Related pages

- [Media library (UI)](/docs/en/user-guide/media-library.md) · [Playlists](/docs/en/user-guide/playlists.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

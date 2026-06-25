---
title: "API: sources"
description: "Storage sources, test, mount, browse."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: sources

> Manage local and SMB sources. Operator+. Passwords write-only/encrypted.

**Audience:** developers / integrators.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/storage-sources` | List sources |
| `POST` | `/api/v1/storage-sources/local` | Create a local source |
| `POST` | `/api/v1/storage-sources/smb` | Create an SMB source |
| `GET/DELETE` | `/api/v1/storage-sources/{id}` | Detail / delete |
| `POST` | `/api/v1/storage-sources/{id}/test` | Test reachability |
| `POST` | `/api/v1/storage-sources/{id}/mount` · `/unmount` | Mount/unmount SMB |
| `GET` | `/api/v1/storage-sources/{id}/browse?subpath=` | Browse a directory |

## Notes

- `browse` is **traversal-protected** (confined to the source path) and flags streamable
  media.
- In-container SMB mounts need elevated privileges – see
  [Storage mounts](/docs/en/admin-guide/storage-mounts.md).
- A failed `test` raises the `source_offline` event
  ([Notifications](/docs/en/user-guide/settings.md)).

## Related pages

- [Sources / storage (UI)](/docs/en/user-guide/sources-storage.md)
- [Media library](/docs/en/api/media-library.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

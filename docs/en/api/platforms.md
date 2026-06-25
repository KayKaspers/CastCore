---
title: "API: platforms & metadata"
description: "Destinations and platform metadata/templates."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: platforms & metadata

> Output destinations (transport) and platform metadata (title/description/thumbnail) are
> separate. Operator+.

**Audience:** developers / integrators.

## Destinations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/destinations[/{id}]` | Destinations; `kind` ∈ platform/rtmp/hls/recording/preview |

`stream_key` is write-only and stored encrypted; responses only show `has_stream_key`.

## Metadata & templates

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/stream-jobs/{id}/metadata` | All platform metadata of a job |
| `PUT/DELETE` | `/api/v1/stream-jobs/{id}/metadata/{platform}` | Create/update/delete |
| `GET` | `/api/v1/stream-jobs/{id}/metadata/{platform}/resolved` | Resolved metadata + warnings |
| `GET` | `/api/v1/metadata/placeholders` | List of placeholders |
| `POST` | `/api/v1/metadata/resolve` | `{template, context}` → resolved text |

## Thumbnails / assets

| Method | Path | Purpose |
| --- | --- | --- |
| `GET/POST/DELETE` | `/api/v1/assets[/{id}]` | Upload/list/delete images |
| `GET` | `/api/v1/assets/{id}/file` | Serve the image file |

Upload validation (magic bytes, size) – see
[Metadata & thumbnails](/docs/en/user-guide/metadata-thumbnails.md).

## Placeholders

`{stream_title} {date} {time} {platform} {category} {tags} {source_name} {server_name} {channel_name}`
([reference](/docs/en/reference/placeholders.md)).

## Related pages

- [Platforms (UI)](/docs/en/user-guide/platforms.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

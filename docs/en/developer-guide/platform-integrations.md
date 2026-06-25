---
title: "Platform integrations"
description: "Platform/metadata layer and how to extend it."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Platform integrations

> How platforms/metadata are implemented and how to extend them.

**Audience:** developers.

## Separating transport and metadata

- **Transport:** `destinations` (URL + stream key) → FFmpeg output.
- **Metadata:** `platform_metadata` per stream job & platform (title/description/tags/
  thumbnail). Resolved via `metadata_service` with
  [placeholders](/docs/en/reference/placeholders.md).

## Adding a platform

1. Allow the platform value (e.g. `kick`) in metadata (frontend selection + validation if
   needed).
2. Optionally add platform-specific hints/warnings in
   `metadata_service.resolve_metadata` (e.g. "category recommended").
3. Update the docs in [Platforms](/docs/en/user-guide/platforms.md) and
   [API: platforms](/docs/en/api/platforms.md).

## Planned (Phase 4)

OAuth integration (connect accounts, store refresh tokens **encrypted**) and API-driven
setting of title/thumbnail.

## Related pages

- [API: platforms & metadata](/docs/en/api/platforms.md) · [Placeholders](/docs/en/reference/placeholders.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

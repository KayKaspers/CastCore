---
title: "Metadata & thumbnails"
description: "Manage platform metadata and description templates with placeholders."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Metadata & thumbnails

> Per stream job and platform you maintain dedicated **metadata** (title, description,
> category, tags, language, visibility, thumbnail). They are resolved and checked before
> start.

**Audience:** users / operators. Invoke: **Stream jobs → Meta**.

## Editing metadata

1. Click **Meta** on a job.
2. Choose the **platform** (Twitch/YouTube/Kick/Facebook/custom). A ✓ marks platforms
   that already have metadata.
3. Fill in: **title**, **category**, **tags**, **language**, **visibility**,
   **description template** and **thumbnail**.
4. **Save**. Use **"resolve preview"** to see the final text.

## Description templates with placeholders

Titles and descriptions may contain [placeholders](/docs/en/reference/placeholders.md),
e.g. `{stream_title}`, `{date}`, `{platform}`, `{source_name}`. Example:

```
Live: {stream_title} on {date} at {time} | Source: {source_name} | #{platform}
```

## Thumbnails & asset library

Manage thumbnails under **Thumbnails / Assets** (`/assets`):

- **Upload image** – allowed: **PNG, JPEG, WebP, GIF** up to **10 MB**.
- In the metadata editor, pick an uploaded asset as the thumbnail per platform.

### Upload security

> 🔐 Uploads are validated by **magic bytes** (not just the extension), size-limited and
> stored under a **generated, safe filename**. The original name never becomes a path on
> disk; assets are never executed.

## Notes

> 💡 The resolution shows **warnings** (e.g. missing thumbnail or category) so you can fix
> them before start.

## Related pages

- [Platforms](/docs/en/user-guide/platforms.md)
- [Placeholders](/docs/en/reference/placeholders.md)
- [API: platforms & metadata](/docs/en/api/platforms.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

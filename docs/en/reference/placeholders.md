---
title: "Placeholders (templates)"
description: "All placeholders for description templates."
lang: en
audience: "All roles"
status: stable
lastReviewed: 2026-06-24
---

# Placeholders (templates)

> In platform **titles** and **description templates** you can use placeholders. Before
> a stream starts, CastCore resolves them and shows the final preview.

**Audience:** anyone maintaining [metadata](/docs/en/user-guide/metadata-thumbnails.md).

## Available placeholders

| Placeholder | Meaning | Example |
| --- | --- | --- |
| `{stream_title}` | name of the stream job | `Gaming Night` |
| `{date}` | current date | `2026-06-24` |
| `{time}` | current time | `20:00` |
| `{platform}` | target platform | `twitch` |
| `{category}` | metadata category | `Just Chatting` |
| `{tags}` | tags, comma-separated | `live, en` |
| `{source_name}` | name/file of the first source | `show.mp4` |
| `{server_name}` | server name (DOMAIN) | `castcore.example.com` |
| `{channel_name}` | channel name (for channels) | `My Channel` |

## Example

**Template:**
```
Live: {stream_title} on {date} at {time} | Source: {source_name} | #{platform}
```
**Resolved:**
```
Live: Gaming Night on 2026-06-24 at 20:00 | Source: show.mp4 | #twitch
```

## Notes

> 💡 `{stream_title}` is always the **job name**, not the platform-specific title
> template – so you can reference `{stream_title}` inside the title itself.

## Related pages

- [Metadata & thumbnails](/docs/en/user-guide/metadata-thumbnails.md)
- [API: platforms & metadata](/docs/en/api/platforms.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

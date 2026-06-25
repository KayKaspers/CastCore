---
title: "Playlists"
description: "Ordered/shuffled media lists as the basis for channels."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Playlists

> A playlist is an ordered or shuffled list of media from the
> [media library](/docs/en/user-guide/media-library.md) – the basis for
> [channels](/docs/en/user-guide/channels.md).

**Audience:** users / operators. UI area: **Playlists** (`/playlists`).

## Create & populate

1. Create a playlist with a **name** and **mode** (`sequential`/`shuffle`/`loop`).
2. On the right, add media from the library (streamable only).
3. Reorder via **▲/▼**, remove entries.

## Modes

| Mode | Behaviour |
| --- | --- |
| **sequential** | fixed order |
| **shuffle** | random order on resolution |
| **loop** | endless repeat (for 24/7 channels) |

## Duration

Use **Duration** and CastCore computes the total length (from the items' ffprobe
durations).

## On to the channel

A playlist is played as continuous playout in a [channel](/docs/en/user-guide/channels.md).

## Related pages

- [Media library](/docs/en/user-guide/media-library.md) · [Channels](/docs/en/user-guide/channels.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

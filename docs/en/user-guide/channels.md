---
title: "Channels (linear playout)"
description: "24/7 channels from playlists with HLS output, EPG and M3U."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Channels (linear playout)

> A **channel** plays a [playlist](/docs/en/user-guide/playlists.md) as a continuous 24/7
> channel (FFmpeg concat + loop) and provides an HLS output plus EPG and M3U export.

**Audience:** users / operators. UI area: **Channels** (`/channels`).

## Step by step

1. Create a [playlist](/docs/en/user-guide/playlists.md) with streamable media.
2. **Create a channel**: name, playlist, optional FFmpeg profile and **fallback video**.
3. Click **Start**. Status is reconciled live (`running`/`stopped`/`failed`).
4. Use the **Outputs** column to open the links:
   - **HLS**: `/api/v1/channels/<id>/hls/index.m3u8`
   - **EPG** (XMLTV): `/api/v1/channels/<id>/epg.xml`
   - **M3U lineup** (all channels): `/api/v1/channels/export.m3u`

## Fallback & robust playout

- On start, **missing files are skipped** – one missing file won't stop the channel.
- If no playlist file is playable and a **fallback video** is set, it loops. Without
  either, the start fails with a clear message.

## EPG & M3U

- **EPG/XMLTV** is generated from item durations as a schedule (now+next).
- **M3U** provides a channel lineup for IPTV players.

## Notes

> ⚠️ In the MVP, the HLS/EPG/M3U endpoints are reachable **without authentication** (for
> players). In production, protect them via the reverse proxy or use signed URLs.

## Related pages

- [Playlists](/docs/en/user-guide/playlists.md)
- [Media library](/docs/en/user-guide/media-library.md)
- [Glossary: HLS, EPG, M3U](/docs/en/reference/glossary.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

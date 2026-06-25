---
title: "Stream editor"
description: "Configure a stream's inputs, outputs, profile and recording."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Stream editor

> In the stream editor you define **what** is streamed (input), **how** (FFmpeg profile)
> and **where to** (output/destination) – optionally with **recording**.

**Audience:** users / operators. UI area: **Stream jobs → Create**.

## Fields

| Field | Meaning |
| --- | --- |
| **Name** | Display name of the job (also `{stream_title}` in metadata). |
| **FFmpeg profile** | Encoding settings, see [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md). |
| **Input URI** | File, device or URL. Use **lavfi** for FFmpeg test sources. |
| **Destination** | Output target ([platform/RTMP/recording](/docs/en/user-guide/platforms.md)). |
| **Format** | `flv` (RTMP), `hls`, `mpegts` (SRT/UDP), `mp4` (recording). |
| **Recording** | Enable a parallel MP4 recording. |

## Step by step

1. Set a **name**.
2. Choose an **input**: local file/path or URL. For a quick test use
   `testsrc=size=1280x720:rate=30` with the **lavfi** option enabled.
3. Choose a **profile** (or default). For pure pass-through use `copy`.
4. Choose a **destination** + **format**.
5. Optionally enable **recording**.
6. Save, then in the list run **Preflight** and **Start**.

## Inputs & outputs

A job can have multiple inputs and multiple outputs (multi-destination). Each active
output is supervised as its own FFmpeg process.

## Notes

> 💡 The easiest way to use a file from the
> [media library](/docs/en/user-guide/media-library.md) is "copy path".

> ⚠️ `copy` (stream copy) only works if source and target are compatible – otherwise use
> an encoding profile (`libx264`/`aac`).

## Related pages

- [Stream jobs](/docs/en/user-guide/streams.md)
- [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)
- [Sources / storage](/docs/en/user-guide/sources-storage.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

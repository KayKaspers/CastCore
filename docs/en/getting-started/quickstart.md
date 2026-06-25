---
title: "Quickstart: your first stream"
description: "From login to your first running test stream in minutes."
lang: en
audience: "Beginners"
status: stable
lastReviewed: 2026-06-24
---

# Quickstart: your first stream

> A safe test stream without an external platform: an FFmpeg test pattern (`lavfi`) is
> written to a local recording file.

**Audience:** beginners.
**Requirements:** signed in, setup complete ([setup wizard](/docs/en/getting-started/first-setup.md)).

## Steps

1. **Create a destination** – *Resources*:
   - Name: `Local recording`, kind: `recording`, URL: `/data/recordings/test.mp4`
2. **Create an FFmpeg profile** – *Resources*:
   - Name: `Test x264`, video codec `libx264` (not "copy"), audio disabled.
3. **Create a stream job** – *Stream jobs* → *Create*:
   - Name: `My test stream`
   - Input URI: `testsrc=size=1280x720:rate=30`, **enable the lavfi checkbox**
   - Pick profile + destination, format `mp4`
4. Click **Preflight** → should be 🟢/🟡.
5. Click **Start**. Use **Live logs** to watch the FFmpeg output in real time.
6. Shortly after, the file appears at `/data/recordings/test.mp4`.

## Next steps

- A real stream to a platform: create a [platform/destination](/docs/en/user-guide/platforms.md)
  with an RTMP URL and stream key.
- Maintain [metadata & description templates](/docs/en/user-guide/metadata-thumbnails.md).
- Add and scan a local or [SMB source](/docs/en/admin-guide/smb-cifs.md).

## Notes

> 💡 `lavfi` sources need no real media – ideal for testing. For real files use the
> [media library](/docs/en/user-guide/media-library.md) and "copy path".

## If something fails

- Stream not starting → [Stream not starting](/docs/en/troubleshooting/stream-not-starting.md)
- FFmpeg errors in the log → [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

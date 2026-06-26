---
title: "FFmpeg errors"
description: "Identify and fix common FFmpeg errors."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-26
---

# FFmpeg errors

> CastCore parses FFmpeg output and shows a **plain-language hint** in the live log.
> This page explains the most common cases.

**Audience:** operators / administrators.

## Symptom: "FFmpeg not found"

**Causes:** FFmpeg is not installed or the path in `.env` (`FFMPEG_PATH`) is wrong.
**Diagnosis:**
```bash
docker compose exec backend ffmpeg -version
```
**Fix:** In Docker, FFmpeg ships in the image. Native: `apt install ffmpeg` and set
`FFMPEG_PATH=/usr/bin/ffmpeg`.

## Symptom: "No such file or directory" (hint: *source/file not found*)

**Causes:** input file missing, mount lost, wrong path.
**Diagnosis:** check the path in the [media library](/docs/en/user-guide/media-library.md);
for network sources check the [mount status](/docs/en/admin-guide/smb-cifs.md).
**Fix:** re-mount the source or use the correct absolute path.

## Symptom: "Invalid data found / could not find codec"

**Causes:** corrupted file or unsupported codec/container.
**Fix:** probe the file with ffprobe, transcode if needed; in the profile do **not** use
`copy` – re-encode (`libx264`/`aac`).

## Symptom: "speed=0.9x" or lower

Real-time isn't kept → [Performance](/docs/en/troubleshooting/performance.md).

## Symptom: RTMP rejected / broken pipe

The platform rejects the connection → usually a wrong stream key or URL.
See [Platform errors](/docs/en/troubleshooting/platform-errors.md).

## "FFmpeg vulnerable" / "Risky codec" (CVE-2026-8461)

- **System status/preflight shows "FFmpeg vulnerable":** the installed FFmpeg version is
  < 8.1.2 and may be affected by CVE-2026-8461 (MagicYUV). Upgrade to a patched build – see
  [FFmpeg requirements & security](/docs/en/admin-guide/ffmpeg-requirements.md).
- **Preflight is "red: risky codec":** the input uses a codec on the blocklist (e.g. MagicYUV).
  With `BLOCK_RISKY_CODECS=true` (default) CastCore blocks the start. Use a different source,
  transcode the file beforehand, or — only if you trust the source and FFmpeg is patched — set
  `BLOCK_RISKY_CODECS=false`.
- **Version unknown:** CastCore could not parse `ffmpeg -version`. Check `FFMPEG_PATH` and that
  the binary is reachable.

## Relevant logs

```bash
docker compose logs -f process-manager     # spawns the FFmpeg processes
```
In the UI: **Stream jobs → Live logs** (error lines are red, with a hint banner).

## Related pages

- [FFmpeg requirements & security](/docs/en/admin-guide/ffmpeg-requirements.md)
- [FFmpeg command builder](/docs/en/developer-guide/ffmpeg-command-builder.md)
- [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)
- [Glossary](/docs/en/reference/glossary.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

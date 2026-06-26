---
title: "FFmpeg requirements & security"
description: "Minimum version, CVE-2026-8461 (MagicYUV), safe-media mode, patch paths."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-26
---

# FFmpeg requirements & security

> CastCore uses **FFmpeg/ffprobe** for stream jobs, media analysis, preflight, channel mode,
> recording and HLS output. Because FFmpeg decodes foreign media, its version is
> security-relevant.

**Audience:** administrators.

## Minimum version

| Component | Minimum version |
| --- | --- |
| FFmpeg | **8.1.2** |
| ffprobe | matching the FFmpeg version (same build) |

CastCore **detects the installed version at runtime** and warns when it is below the minimum
(system status, preflight, setup wizard).

## CVE-2026-8461 ("PixelSmash", MagicYUV)

Per the advisory, the vulnerability affects the **MagicYUV decoder in libavcodec** in FFmpeg
versions **before 8.1.2**. A crafted media file can, in certain scenarios, lead to remote
code execution during decoding.

> ℹ️ The exact details (affected versions, codec) come from the operator-provided advisory –
> verify against authoritative sources (NVD) for your environment.

**Assessment for CastCore:** FFmpeg decodes configured inputs (stream jobs, dry-run) and
analyses files during media scans (ffprobe, including from SMB sources). Automatic thumbnail
generation is not active yet. ffprobe/dry-run/preflight run with **timeouts**.

## Mitigations in CastCore

- **Version detection & warnings** in the system status (`Monitoring`), **preflight** and the
  **setup wizard**.
- **Safe-media mode**: risky codecs are detected and — depending on configuration — blocked at
  stream start or shown as a warning. MagicYUV is listed by default.
- **Media library**: files with a risky codec get a **"Risky codec"** badge.
- **Process hardening**: FFmpeg processes get a **minimal, secret-free environment**; compose
  services run with `no-new-privileges`, and the worker additionally `cap_drop: ALL` and as a
  **non-root** user. See [Security best practices](/docs/en/admin-guide/security.md).

Relevant settings (see [Environment variables](/docs/en/reference/environment-variables.md)):
`SAFE_MEDIA_PROCESSING_ENABLED`, `MEDIA_AUTOTHUMBNAILS_ENABLED`, `BLOCK_RISKY_CODECS`,
`RISKY_CODECS_BLOCKLIST`.

## Providing a patched FFmpeg

If your distribution only ships an older FFmpeg, there are several options:

1. **Official static build** (e.g. from a trusted provider) – the Docker images support this
   via a build argument:
   ```bash
   docker compose build \
     --build-arg FFMPEG_VARIANT=static \
     --build-arg FFMPEG_STATIC_URL=<url to an 8.1.2+ tarball>
   ```
   The archive must contain `ffmpeg`/`ffprobe` (optionally under `bin/`); they install to
   `/usr/bin`.
2. **Custom container** with a safe FFmpeg version (base image or multi-stage build).
3. **Distribution package source / backport** (if a patched package is available).
4. **Temporary risk reduction** until a patch is available: `BLOCK_RISKY_CODECS=true`
   (default) makes CastCore block streams with risky codecs as **red** in preflight.

## Related pages

- [Security best practices](/docs/en/admin-guide/security.md)
- [Environment variables](/docs/en/reference/environment-variables.md)
- [Preflight checks](/docs/en/user-guide/preflight-checks.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

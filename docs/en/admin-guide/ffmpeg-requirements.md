---
title: "FFmpeg requirements & security"
description: "Minimum version, CVE-2026-8461 (MagicYUV), safe-media mode, patch paths."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-29
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

## How the Docker images obtain FFmpeg (build variants)

The Docker images (backend, process-manager, worker) select how FFmpeg/ffprobe are provided via
the build argument **`FFMPEG_VARIANT`** (configurable in `.env`). All three images use the **same**
version.

| Variant | Source | Min-version build gate | Recommended |
| --- | --- | --- | --- |
| **`copy`** (default) | Multi-stage `COPY` from a **pinned, static** image (`FFMPEG_IMAGE`, tag **+ digest**) | ✅ build fails if `< 8.1.2` | ✅ **Yes** |
| **`static`** | Download a static tarball (`FFMPEG_STATIC_URL`) and verify `FFMPEG_STATIC_SHA256` | ✅ build fails if `< 8.1.2` | For custom mirrors |
| **`apt`** | Debian package | ❌ no gate (may be `< 8.1.2`) | ❌ Fallback only |

The default `copy` build pins **`mwader/static-ffmpeg:8.1.2@sha256:…`** (static, self-contained
`ffmpeg`/`ffprobe`, amd64 + arm64). The pin uses a **tag and a digest** — never a bare tag or
`latest`. Binaries always install to `/usr/bin`, so `FFMPEG_PATH`/`FFPROBE_PATH` stay unchanged.

```bash
# Default (recommended): pinned static 8.1.2 image, build-gated
docker compose build

# Custom static tarball (must be >= 8.1.2); the build verifies the checksum
docker compose build \
  --build-arg FFMPEG_VARIANT=static \
  --build-arg FFMPEG_STATIC_URL=<url to an 8.1.2+ tarball> \
  --build-arg FFMPEG_STATIC_SHA256=<sha256 of that tarball>

# Fallback to Debian's package (NOT recommended; may be < 8.1.2, runtime will warn)
docker compose build --build-arg FFMPEG_VARIANT=apt
```

> 🔒 For `copy`/`static` the image build **fails** if the resulting `ffmpeg`/`ffprobe` is below
> 8.1.2 (checked via `ffmpeg -version` / `ffprobe -version` during build).

**License note:** static FFmpeg builds are typically **GPL** (they include GPL components such as
x264/x265). You may use them with CastCore, but if you redistribute the images, comply with the
GPL terms of the bundled FFmpeg build.

**GPU encoding:** a static FFmpeg build **does not** make NVENC/QSV/VAAPI work automatically.
Hardware encoding additionally requires the matching host drivers and a GPU-enabled container
runtime (NVIDIA Container Toolkit, or `/dev/dri` for VAAPI). GPU encoding is handled as a
separate feature; see the roadmap.

### Other options

- **Custom container / multi-stage build** with your own verified FFmpeg.
- **Distribution backport** (if a patched package is available) — then use `FFMPEG_VARIANT=apt`.
- **Temporary risk reduction** until patched: `BLOCK_RISKY_CODECS=true` (default) makes CastCore
  block streams with risky codecs as **red** in preflight.
- **Native install** (`scripts/install.sh`) uses the distro's FFmpeg and **warns** when it is
  below 8.1.2; pass `--require-safe-ffmpeg` (or `CASTCORE_REQUIRE_SAFE_FFMPEG=true`) to make it
  **abort** instead.

## Related pages

- [Security best practices](/docs/en/admin-guide/security.md)
- [Environment variables](/docs/en/reference/environment-variables.md)
- [Preflight checks](/docs/en/user-guide/preflight-checks.md)

---
_Last reviewed: 2026-06-29 · Status: stable_

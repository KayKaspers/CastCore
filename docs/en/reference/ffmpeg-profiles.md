---
title: "FFmpeg profiles"
description: "Fields of an FFmpeg profile and their effect."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# FFmpeg profiles

> An FFmpeg profile bundles the **encoding settings** a stream job or channel uses. Edit
> it under **FFmpeg profiles** (`/profiles`).

**Audience:** users / operators.

## Stream copy vs. re-encode

- **Stream copy** (`copy_mode`): passes video/audio through **without re-encoding**
  (`-c copy`). Very light on resources, but only works if source and target are compatible.
- **Re-encode**: encodes anew – needed for fixed resolution/bitrate, filters, or when the
  source isn't target-compatible.

## Video fields

| Field | Meaning |
| --- | --- |
| **Codec** | `libx264`, `libx265`, GPU: `h264_nvenc`, `hevc_nvenc`, `h264_qsv`, `h264_vaapi`, plus `libvpx-vp9`, `libaom-av1`. |
| **Bitrate** | Target video bitrate, e.g. `6000k`. |
| **Width × height** | Output resolution (scaling). |
| **FPS** | Frame rate. |
| **Preset** | Speed/quality (x264/x265): `ultrafast` … `veryslow`. |
| **Tune** | Fine-tuning, e.g. `zerolatency`. |
| **GOP / keyframe** | Keyframe interval in frames (e.g. `60`). Important for HLS/latency. |
| **Pixel format** | e.g. `yuv420p` (broad compatibility), `nv12`, `p010le`. |

## Audio fields

| Field | Meaning |
| --- | --- |
| **Codec** | `aac`, `libfdk_aac`, `libmp3lame`, `libopus`, `ac3`. |
| **Bitrate** | e.g. `160k`. |
| **Disable audio** | No audio (`-an`). |

## Advanced

- **Filter (`filter_complex`)**: FFmpeg filter chain, e.g. `scale=1280:720`.
- **Expert parameters**: additional, space-separated arguments, e.g.
  `-rc cbr -bufsize 12000k`. These are passed through deliberately.

> 🔐 All values are validated and passed to FFmpeg as an **argument list** (no shell).
> See [FFmpeg command builder](/docs/en/developer-guide/ffmpeg-command-builder.md).

## GPU encoding (NVENC / QSV / VAAPI)

If you pick a GPU codec, the **target machine** must have matching drivers/devices
(NVIDIA GPU + NVENC, Intel QuickSync, or VAAPI). Under Docker, the GPU devices must also
be passed into the container. "Preset" values are encoder-specific.

## Preview

Use **command preview** to see how the profile looks as an FFmpeg command (with the
stream key masked).

## Related pages

- [Stream editor](/docs/en/user-guide/stream-editor.md)
- [Glossary](/docs/en/reference/glossary.md)
- [Performance](/docs/en/troubleshooting/performance.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

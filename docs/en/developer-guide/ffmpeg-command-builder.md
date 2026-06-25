---
title: "FFmpeg command builder"
description: "Safe argv construction without a shell."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# FFmpeg command builder

> Security-critical core module: `app/services/ffmpeg/command_builder.py`. Builds FFmpeg
> invocations as **argument lists** – **never** a shell string.

**Audience:** developers.

## Guarantees

- Correct order: global options → input options → input → filters → output options → output.
- **Validation/whitelist** for codecs (incl. GPU: nvenc/qsv/vaapi), presets, pixel formats.
- Multiple inputs/outputs, HLS/RTMP/SRT, stream copy vs. re-encode, loop, reconnect.
- **Secret masking** in the preview (stream keys in URLs).
- No shell: handed to `asyncio.create_subprocess_exec(*argv)` (`shell=False`).

## Types

`FFmpegCommand(inputs=[Input…], outputs=[Output…], filter_complex, expert_args)` →
`.build()` (argv) and `.preview()` (masked string). `Input`/`Output` encapsulate options.

## Validation

Unsafe characters in structured fields are rejected (`CommandBuildError` → HTTP 400).
Expert parameters go through a separate, validated channel.

## Tests

`backend/tests/ffmpeg/test_command_builder.py` covers ordering, copy/re-encode,
multi-output, reconnect, injection defence and masking.

## Related pages

- [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md) · [Process manager](/docs/en/developer-guide/process-manager.md)
- [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

---
title: "FFmpeg Command Builder"
description: "Sichere argv-Konstruktion ohne Shell."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# FFmpeg Command Builder

> Sicherheitskritisches Kernmodul: `app/services/ffmpeg/command_builder.py`. Baut
> FFmpeg-Aufrufe als **Argumentlisten** – **niemals** als Shell-String.

**Zielgruppe:** Entwickler.

## Garantien

- Korrekte Reihenfolge: globale Optionen → Input-Optionen → Input → Filter →
  Output-Optionen → Output.
- **Validierung/Whitelist** für Codecs (inkl. GPU: nvenc/qsv/vaapi), Presets, Pixel-Formate.
- Mehrere Inputs/Outputs, HLS/RTMP/SRT, Stream-Copy vs. Re-Encode, Loop, Reconnect.
- **Secret-Masking** in der Vorschau (Stream-Keys in URLs).
- Keine Shell: Übergabe an `asyncio.create_subprocess_exec(*argv)` (`shell=False`).

## Datentypen

`FFmpegCommand(inputs=[Input…], outputs=[Output…], filter_complex, expert_args)` →
`.build()` (argv) bzw. `.preview()` (maskierter String). `Input`/`Output` kapseln Optionen.

## Validierung

Unsichere Zeichen in strukturierten Feldern werden abgewiesen (`CommandBuildError`,
→ HTTP 400). Experten-Parameter laufen über einen separaten, geprüften Kanal.

## Tests

`backend/tests/ffmpeg/test_command_builder.py` deckt Reihenfolge, Copy/Re-Encode,
Multi-Output, Reconnect, Injection-Abwehr und Masking ab.

## Verwandte Seiten

- [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md) · [Process Manager](/docs/de/developer-guide/process-manager.md)
- [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md)

---
_Stand: 2026-06-24 · Status: Stabil_

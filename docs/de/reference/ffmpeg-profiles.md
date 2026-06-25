---
title: "FFmpeg-Profile"
description: "Felder eines FFmpeg-Profils und ihre Wirkung."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# FFmpeg-Profile

> Ein FFmpeg-Profil bündelt die **Encoding-Einstellungen**, die ein Stream-Job oder
> Channel verwendet. Bearbeitet wird es unter **FFmpeg-Profile** (`/profiles`).

**Zielgruppe:** Anwender / Operatoren.

## Stream Copy vs. Re-Encode

- **Stream Copy** (`copy_mode`): reicht Video/Audio **ohne Neukodierung** durch
  (`-c copy`). Sehr ressourcenschonend, funktioniert aber nur, wenn Quelle und Ziel
  kompatibel sind.
- **Re-Encode**: kodiert neu – nötig für feste Auflösung/Bitrate, Filter oder wenn die
  Quelle nicht zielkompatibel ist.

## Video-Felder

| Feld | Bedeutung |
| --- | --- |
| **Codec** | `libx264`, `libx265`, GPU: `h264_nvenc`, `hevc_nvenc`, `h264_qsv`, `h264_vaapi`, sowie `libvpx-vp9`, `libaom-av1`. |
| **Bitrate** | Ziel-Videobitrate, z. B. `6000k`. |
| **Breite × Höhe** | Ausgabeauflösung (Skalierung). |
| **FPS** | Bildrate. |
| **Preset** | Geschwindigkeit/Qualität (x264/x265): `ultrafast` … `veryslow`. |
| **Tune** | Feinabstimmung, z. B. `zerolatency`. |
| **GOP / Keyframe** | Keyframe-Intervall in Frames (z. B. `60`). Wichtig für HLS/Latenz. |
| **Pixel-Format** | z. B. `yuv420p` (breite Kompatibilität), `nv12`, `p010le`. |

## Audio-Felder

| Feld | Bedeutung |
| --- | --- |
| **Codec** | `aac`, `libfdk_aac`, `libmp3lame`, `libopus`, `ac3`. |
| **Bitrate** | z. B. `160k`. |
| **Audio deaktivieren** | Kein Audio (`-an`). |

## Erweitert

- **Filter (`filter_complex`)**: FFmpeg-Filterkette, z. B. `scale=1280:720`.
- **Experten-Parameter**: zusätzliche, leerzeichengetrennte Argumente, z. B.
  `-rc cbr -bufsize 12000k`. Diese werden bewusst durchgereicht.

> 🔐 Alle Werte werden validiert und als **Argumentliste** an FFmpeg übergeben (keine
> Shell). Siehe [FFmpeg Command Builder](/docs/de/developer-guide/ffmpeg-command-builder.md).

## GPU-Encoding (NVENC / QSV / VAAPI)

Wählst du einen GPU-Codec, muss die **Zielmaschine** passende Treiber/Geräte besitzen
(NVIDIA-GPU + NVENC, Intel QuickSync, oder VAAPI). Im Docker-Betrieb müssen die
GPU-Geräte zusätzlich in den Container durchgereicht werden. Die „Preset"-Werte gelten
encoder-abhängig.

## Vorschau

Über **Command-Vorschau** siehst du, wie das Profil als FFmpeg-Befehl aussieht
(mit maskiertem Stream-Key).

## Verwandte Seiten

- [Stream-Editor](/docs/de/user-guide/stream-editor.md)
- [Glossar](/docs/de/reference/glossary.md)
- [Performance](/docs/de/troubleshooting/performance.md)

---
_Stand: 2026-06-24 · Status: Stabil_

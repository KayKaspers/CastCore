---
title: "Performance"
description: "Encoding-Speed < 1.0x, hohe CPU, Engpässe."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Performance

> Wenn die Maschine den Stream nicht in Echtzeit schafft oder die Last zu hoch ist.

**Zielgruppe:** Operatoren / Administratoren.

## Symptom: Encoding-Speed < 1.0×

**Bedeutung:** FFmpeg kodiert langsamer als Echtzeit → der Stream stockt/fällt zurück.
**Mögliche Ursachen:** zu hohe Auflösung/Bitrate, zu langsames Preset, CPU überlastet,
mehrere parallele Streams.
**Lösung:**

- Im [FFmpeg-Profil](/docs/de/reference/ffmpeg-profiles.md) ein **schnelleres Preset**
  (z. B. `veryfast`/`ultrafast`) und/oder **niedrigere Auflösung/Bitrate** wählen.
- **GPU-Encoder** (NVENC/QSV/VAAPI) nutzen, falls Hardware vorhanden.
- Anzahl paralleler Streams reduzieren.

## Symptom: hohe CPU-Last

**Diagnose:** [Monitoring](/docs/de/user-guide/monitoring.md) – CPU pro Output und gesamt.
**Lösung:** wie oben; Stream Copy nutzen, wo möglich (kein Re-Encode).

## Vorab prüfen

Mit dem [Dry-Run](/docs/de/user-guide/preflight-checks.md) schätzt du die Encoding-Speed,
**bevor** du live gehst.

## Relevante Werte

- **speed** (×), **fps**, **CPU%**, **RAM** pro Output im Monitoring.
- Dropped Frames, sofern ermittelbar.

## Verwandte Seiten

- [Monitoring](/docs/de/user-guide/monitoring.md)
- [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)
- [Systemanforderungen](/docs/de/admin-guide/system-requirements.md)

---
_Stand: 2026-06-24 · Status: Stabil_

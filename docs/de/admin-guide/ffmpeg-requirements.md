---
title: "FFmpeg-Anforderungen & Sicherheit"
description: "Mindestversion, CVE-2026-8461 (MagicYUV), Safe-Media-Modus, Patch-Wege."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-26
---

# FFmpeg-Anforderungen & Sicherheit

> CastCore nutzt **FFmpeg/ffprobe** für Stream-Jobs, Medienanalyse, Preflight, Channel Mode,
> Recording und HLS-Ausgabe. Da FFmpeg fremde Mediendaten dekodiert, ist die Version
> sicherheitsrelevant.

**Zielgruppe:** Administratoren.

## Mindestversion

| Komponente | Mindestversion |
| --- | --- |
| FFmpeg | **8.1.2** |
| ffprobe | passend zur FFmpeg-Version (gleiches Build) |

CastCore **erkennt die installierte Version zur Laufzeit** und warnt, wenn sie darunter liegt
(Systemstatus, Preflight, Setup-Assistent).

## CVE-2026-8461 ("PixelSmash", MagicYUV)

Laut Meldung betrifft die Schwachstelle den **MagicYUV-Decoder in libavcodec** in FFmpeg-
Versionen **vor 8.1.2**. Eine präparierte Mediendatei kann beim Dekodieren in bestimmten
Szenarien zu Remote Code Execution führen.

> ℹ️ Die genauen Angaben (betroffene Versionen, Codec) stammen aus der Betreibermeldung –
> bitte gegen autoritative Quellen (NVD) für deine Umgebung prüfen.

**Bewertung für CastCore:** FFmpeg dekodiert konfigurierte Eingänge (Stream-Jobs, Dry-Run)
und analysiert Dateien beim Medien-Scan (ffprobe, auch von SMB-Quellen). Automatische
Thumbnail-Erzeugung ist derzeit noch nicht aktiv. ffprobe/Dry-Run/Preflight laufen mit
**Timeouts**.

## Schutzmaßnahmen in CastCore

- **Versionserkennung & Warnungen** in Systemstatus (`Monitoring`), **Preflight** und
  **Setup-Assistent**.
- **Safe-Media-Modus**: riskante Codecs werden erkannt und – je nach Konfiguration – beim
  Stream-Start blockiert oder als Warnung angezeigt. MagicYUV ist standardmäßig gelistet.
- **Medienbibliothek**: Dateien mit riskantem Codec erhalten ein Badge **„Riskanter Codec"**.
- **Prozess-Härtung**: FFmpeg-Prozesse erhalten ein **minimales Environment ohne Secrets**;
  Compose-Dienste laufen mit `no-new-privileges`, der Worker zusätzlich `cap_drop: ALL` und
  als **Nicht-Root**. Siehe [Security Best Practices](/docs/de/admin-guide/security.md).

Relevante Einstellungen (siehe [Umgebungsvariablen](/docs/de/reference/environment-variables.md)):
`SAFE_MEDIA_PROCESSING_ENABLED`, `MEDIA_AUTOTHUMBNAILS_ENABLED`, `BLOCK_RISKY_CODECS`,
`RISKY_CODECS_BLOCKLIST`.

## Eine gepatchte FFmpeg-Version bereitstellen

Liefert deine Distribution nur ein älteres FFmpeg, gibt es mehrere Wege:

1. **Offizielles statisches Build** (z. B. von einem vertrauenswürdigen Anbieter) – die
   Docker-Images unterstützen das per Build-Argument:
   ```bash
   docker compose build \
     --build-arg FFMPEG_VARIANT=static \
     --build-arg FFMPEG_STATIC_URL=<URL eines 8.1.2+-Tarballs>
   ```
   Das Archiv muss `ffmpeg`/`ffprobe` enthalten (optional unter `bin/`); sie werden nach
   `/usr/bin` installiert.
2. **Eigener Container** mit einer sicheren FFmpeg-Version (Basis-Image oder Multi-Stage-Build).
3. **Paketquelle/Backport** der Distribution (sofern ein gepatchtes Paket verfügbar ist).
4. **Temporäre Risikoreduktion**, bis ein Patch verfügbar ist: `BLOCK_RISKY_CODECS=true`
   (Standard) lässt CastCore Streams mit riskanten Codecs im Preflight als **rot** blockieren.

## Verwandte Seiten

- [Security Best Practices](/docs/de/admin-guide/security.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)
- [Preflight-Checks](/docs/de/user-guide/preflight-checks.md)

---
_Stand: 2026-06-26 · Status: Stabil_

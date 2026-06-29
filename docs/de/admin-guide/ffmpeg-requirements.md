---
title: "FFmpeg-Anforderungen & Sicherheit"
description: "Mindestversion, CVE-2026-8461 (MagicYUV), Safe-Media-Modus, Patch-Wege."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-29
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

## Wie die Docker-Images FFmpeg beziehen (Build-Varianten)

Die Docker-Images (Backend, Process-Manager, Worker) wählen über das Build-Argument
**`FFMPEG_VARIANT`** (in `.env` konfigurierbar), wie FFmpeg/ffprobe bereitgestellt werden. Alle
drei Images nutzen **dieselbe** Version.

| Variante | Quelle | Build-Gate Mindestversion | Empfohlen |
| --- | --- | --- | --- |
| **`copy`** (Default) | Multi-Stage-`COPY` aus einem **gepinnten, statischen** Image (`FFMPEG_IMAGE`, Tag **+ Digest**) | ✅ Build bricht ab bei `< 8.1.2` | ✅ **Ja** |
| **`static`** | Static-Tarball laden (`FFMPEG_STATIC_URL`) und `FFMPEG_STATIC_SHA256` prüfen | ✅ Build bricht ab bei `< 8.1.2` | Für eigene Mirror |
| **`apt`** | Debian-Paket | ❌ kein Gate (ggf. `< 8.1.2`) | ❌ nur Fallback |

Der Default `copy` pinnt **`mwader/static-ffmpeg:8.1.2@sha256:…`** (statisch, eigenständige
`ffmpeg`/`ffprobe`, amd64 + arm64). Der Pin nutzt **Tag und Digest** – nie ein nacktes Tag oder
`latest`. Die Binaries landen immer in `/usr/bin`, daher bleiben `FFMPEG_PATH`/`FFPROBE_PATH`
unverändert.

```bash
# Default (empfohlen): gepinntes statisches 8.1.2-Image, mit Build-Gate
docker compose build

# Eigener Static-Tarball (muss >= 8.1.2 sein); der Build prüft die Checksumme
docker compose build \
  --build-arg FFMPEG_VARIANT=static \
  --build-arg FFMPEG_STATIC_URL=<URL eines 8.1.2+-Tarballs> \
  --build-arg FFMPEG_STATIC_SHA256=<SHA256 des Tarballs>

# Fallback auf das Debian-Paket (NICHT empfohlen; ggf. < 8.1.2, Laufzeit warnt)
docker compose build --build-arg FFMPEG_VARIANT=apt
```

> 🔒 Bei `copy`/`static` **schlägt der Build fehl**, wenn das resultierende `ffmpeg`/`ffprobe`
> unter 8.1.2 liegt (geprüft per `ffmpeg -version` / `ffprobe -version` während des Builds).

**Lizenzhinweis:** Statische FFmpeg-Builds sind in der Regel **GPL** (sie enthalten GPL-
Komponenten wie x264/x265). Die Nutzung mit CastCore ist erlaubt; bei Weiterverbreitung der
Images sind die GPL-Bedingungen des enthaltenen FFmpeg-Builds einzuhalten.

**GPU-Encoding:** Ein statischer FFmpeg-Build lässt NVENC/QSV/VAAPI **nicht** automatisch
funktionieren. Hardware-Encoding braucht zusätzlich passende Host-Treiber und eine GPU-fähige
Container-Runtime (NVIDIA Container Toolkit bzw. `/dev/dri` für VAAPI). GPU-Encoding ist ein
separates Feature; siehe Roadmap.

### Weitere Wege

- **Eigener Container / Multi-Stage-Build** mit eigener verifizierter FFmpeg-Version.
- **Distributions-Backport** (sofern gepatchtes Paket verfügbar) – dann `FFMPEG_VARIANT=apt`.
- **Temporäre Risikoreduktion**, bis gepatcht: `BLOCK_RISKY_CODECS=true` (Standard) lässt
  CastCore Streams mit riskanten Codecs im Preflight als **rot** blockieren.
- **Native Installation** (`scripts/install.sh`) nutzt das Distro-FFmpeg und **warnt** bei
  < 8.1.2; mit `--require-safe-ffmpeg` (oder `CASTCORE_REQUIRE_SAFE_FFMPEG=true`) **bricht** sie
  stattdessen ab.

## Verwandte Seiten

- [Security Best Practices](/docs/de/admin-guide/security.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)
- [Preflight-Checks](/docs/de/user-guide/preflight-checks.md)

---
_Stand: 2026-06-29 · Status: Stabil_

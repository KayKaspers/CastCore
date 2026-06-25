---
title: "Medienbibliothek (Entwickler)"
description: "Scan-/ffprobe-Pipeline der Medienbibliothek."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Medienbibliothek (Entwickler)

> Aufbau der Scan-/Index-Pipeline. Bedienung: [Medienbibliothek](/docs/de/user-guide/media-library.md).

**Zielgruppe:** Entwickler.

## Pipeline

`media_service.scan_source(db, source)`:

1. Läuft über den effektiven Pfad der Quelle (`os.walk`).
2. Klassifiziert per Endung (`video`/`audio`/`image`/`other`), erfasst Größe/mtime.
3. **Inkrementell:** unveränderte Dateien (Größe + mtime) werden übersprungen.
4. Für Medien: **ffprobe** (JSON) → Container/Codecs/Auflösung/FPS/Bitrate in
   `media_probe_data`; setzt `streamable` + `problem_flags`.

## Modelle

`media_library_items` (1:1) `media_probe_data`. Unique pro `(storage_source_id, rel_path)`.

## Wiederverwendung

Die Funktion ist zustandslos bzgl. Transport und kann später vom **Worker** (arq) für
große Bibliotheken im Hintergrund aufgerufen werden.

## ffprobe

Aufruf als Argumentliste (`-v error -print_format json -show_streams -show_format`),
Timeout pro Datei.

## Verwandte Seiten

- [Medienbibliothek (UI)](/docs/de/user-guide/media-library.md) · [API: Medienbibliothek](/docs/de/api/media-library.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Medienbibliothek"
description: "Quellen scannen, Medien per ffprobe indexieren und als Input wählen."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Medienbibliothek

> Die Medienbibliothek scannt deine Quellen, analysiert jede Datei mit **ffprobe** und
> macht sie durchsuchbar und als Stream-Input verfügbar.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Medienbibliothek** (`/media`).

## Schritt für Schritt

1. Oben eine **Quelle** wählen (aus [Quellen/Storage](/docs/de/user-guide/sources-storage.md)).
2. **Scan** klicken. CastCore durchläuft die Dateien, indexiert sie und liest per
   ffprobe Codec, Auflösung, Framerate, Dauer und Bitrate aus.
3. Über **Suche** und den Filter **„nur streamfähig"** die Liste eingrenzen.
4. Bei einer Datei **„copy path"** klicken und den Pfad im
   [Stream-Editor](/docs/de/user-guide/stream-editor.md) oder in einer
   [Playlist](/docs/de/user-guide/playlists.md) verwenden.

## Spalten

| Spalte | Bedeutung |
| --- | --- |
| **Datei** | Dateiname + relativer Pfad; Badge **stream** = streamfähig. |
| **Codec** | Video-/Audio-Codec aus ffprobe. |
| **Auflösung** | Breite × Höhe (+ FPS). |
| **Dauer / Größe** | Länge und Dateigröße. |

## Hinweise

> 💡 Der Scan ist **inkrementell** – unveränderte Dateien werden übersprungen.

> ⚠️ Als nicht streamfähig markierte Dateien fehlen meist Video/Audio oder sind nicht
> lesbar → siehe [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md).

## Verwandte Seiten

- [Quellen / Storage](/docs/de/user-guide/sources-storage.md)
- [Playlists](/docs/de/user-guide/playlists.md)
- [Stream-Editor](/docs/de/user-guide/stream-editor.md)

---
_Stand: 2026-06-24 · Status: Stabil_

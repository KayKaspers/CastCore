---
title: "Stream-Editor"
description: "Inputs, Outputs, Profil und Recording eines Streams konfigurieren."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Stream-Editor

> Im Stream-Editor legst du fest, **was** gestreamt wird (Input), **wie** (FFmpeg-Profil)
> und **wohin** (Output/Destination) – optional mit **Recording**.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Stream-Jobs → Erstellen**.

## Felder

| Feld | Bedeutung |
| --- | --- |
| **Name** | Anzeigename des Jobs (auch `{stream_title}` in Metadaten). |
| **FFmpeg-Profil** | Encoding-Einstellungen, siehe [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md). |
| **Input-URI** | Datei, Gerät oder URL. Mit **lavfi** für FFmpeg-Testquellen. |
| **Destination** | Ausgabeziel ([Plattform/RTMP/Recording](/docs/de/user-guide/platforms.md)). |
| **Format** | `flv` (RTMP), `hls`, `mpegts` (SRT/UDP), `mp4` (Aufnahme). |
| **Recording** | Parallele Aufnahme als MP4 aktivieren. |

## Schritt für Schritt

1. **Name** vergeben.
2. **Input** wählen: lokale Datei/Pfad oder URL. Für einen schnellen Test
   `testsrc=size=1280x720:rate=30` mit aktivierter **lavfi**-Option.
3. **Profil** wählen (oder Standard). Für reine Weiterleitung ohne Neukodierung `copy`.
4. **Destination** + **Format** wählen.
5. Optional **Recording** aktivieren.
6. Speichern, dann in der Liste **Preflight** und **Start**.

## Inputs & Outputs

Ein Job kann mehrere Inputs und mehrere Outputs haben (Multi-Destination). Jeder aktive
Output wird als eigener FFmpeg-Prozess überwacht.

## Hinweise

> 💡 Eine Eingabe aus der [Medienbibliothek](/docs/de/user-guide/media-library.md)
> übernimmst du am einfachsten per „copy path".

> ⚠️ `copy` (Stream Copy) funktioniert nur, wenn Quelle und Ziel kompatibel sind –
> sonst ein Encoding-Profil (`libx264`/`aac`) verwenden.

## Verwandte Seiten

- [Stream-Jobs](/docs/de/user-guide/streams.md)
- [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)
- [Quellen / Storage](/docs/de/user-guide/sources-storage.md)

---
_Stand: 2026-06-24 · Status: Stabil_

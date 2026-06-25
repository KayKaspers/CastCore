---
title: "Schnellstart: Erster Stream"
description: "In wenigen Minuten vom Login zum ersten laufenden Teststream."
lang: de
audience: "Einsteiger"
status: stable
lastReviewed: 2026-06-24
---

# Schnellstart: Erster Stream

> Ein sicherer Teststream ohne externe Plattform: ein FFmpeg-Testbild (`lavfi`) wird in
> eine lokale Aufnahmedatei geschrieben.

**Zielgruppe:** Einsteiger.
**Voraussetzungen:** Angemeldet, Setup abgeschlossen ([Setup-Assistent](/docs/de/getting-started/first-setup.md)).

## Schritte

1. **Ziel (Destination) anlegen** – Bereich *Resources*:
   - Name: `Lokale Aufnahme`, Kind: `recording`, URL: `/data/recordings/test.mp4`
2. **FFmpeg-Profil anlegen** – Bereich *Resources*:
   - Name: `Test x264`, Video-Codec `libx264` (nicht „copy"), Audio deaktiviert.
3. **Stream-Job anlegen** – Bereich *Stream-Jobs* → *Erstellen*:
   - Name: `Mein Teststream`
   - Input-URI: `testsrc=size=1280x720:rate=30`, **lavfi-Checkbox aktivieren**
   - Profil + Destination wählen, Format `mp4`
4. **Preflight** klicken → sollte 🟢/🟡 sein.
5. **Start** klicken. Über **Live-Logs** siehst du die FFmpeg-Ausgabe in Echtzeit.
6. Nach kurzer Zeit liegt die Datei unter `/data/recordings/test.mp4`.

## Nächste Schritte

- Echten Stream zu einer Plattform: lege eine [Plattform/Destination](/docs/de/user-guide/platforms.md)
  mit RTMP-URL und Stream-Key an.
- [Metadaten & Beschreibungsvorlagen](/docs/de/user-guide/metadata-thumbnails.md) pflegen.
- Eine lokale oder [SMB-Quelle](/docs/de/admin-guide/smb-cifs.md) einbinden und scannen.

## Hinweise

> 💡 `lavfi`-Quellen brauchen kein echtes Medium – ideal zum Testen. Für reale Dateien
> die [Medienbibliothek](/docs/de/user-guide/media-library.md) nutzen und „copy path".

## Bei Problemen

- Stream startet nicht → [Stream startet nicht](/docs/de/troubleshooting/stream-not-starting.md)
- FFmpeg-Fehler im Log → [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md)

---
_Stand: 2026-06-24 · Status: Stabil_

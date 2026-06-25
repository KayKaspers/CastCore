---
title: "Was ist CastCore?"
description: "Überblick über Zweck, Zielgruppe und Funktionsumfang von CastCore."
lang: de
audience: "Einsteiger"
status: stable
lastReviewed: 2026-06-24
---

# Was ist CastCore?

> CastCore ist eine **selbst gehostete Streaming Operations Suite** – eine Steuerzentrale
> (Control Plane) für FFmpeg-Streams, Medienquellen, Storage, Plattform-Metadaten,
> Multi-Output-Streaming, Monitoring, Recording und lineare Channels.

**Zielgruppe:** Einsteiger und Entscheider, die verstehen wollen, was CastCore leistet.

## Für wen ist CastCore?

- **Streamer & Creator**, die mehrere Plattformen gleichzeitig bespielen wollen.
- **Vereine, Sender, Communities**, die eigene 24/7-Kanäle betreiben möchten.
- **Administratoren**, die Streaming zentral, sicher und nachvollziehbar verwalten wollen.

## Was kann CastCore?

- **Stream-Jobs**: FFmpeg-Streams sicher anlegen, starten, stoppen, überwachen.
- **Multi-Output**: ein Stream → mehrere Ziele (Twitch, YouTube, eigener RTMP, Recording).
- **Quellen & Storage**: lokale Dateien, SMB/CIFS, später NFS/Cloud.
- **Medienbibliothek**: Quellen scannen, per ffprobe analysieren, als Input wählen.
- **Channels**: lineare 24/7-Kanäle aus Playlists mit HLS-Output, EPG und M3U.
- **Plattform-Metadaten**: Titel/Beschreibung/Tags mit [Platzhaltern](/docs/de/reference/placeholders.md).
- **Monitoring**: CPU, RAM, FPS, Bitrate – live pro Stream.
- **Recording & Replay**, **Preflight-Checks**, **Benachrichtigungen**, **Scheduler**, **Backup/Restore**.

## Was CastCore *nicht* ist

CastCore ist kein einfacher „FFmpeg-Webwrapper". Es ist eine **Operations-Suite**:
Quellen verwalten, Medien analysieren, Streams planen, FFmpeg sicher steuern, Fehler
verständlich erklären und den Betrieb vereinfachen.

## Nächste Schritte

- [Installation mit Docker Compose](/docs/de/getting-started/installation-docker.md)
- [Setup-Assistent](/docs/de/getting-started/first-setup.md)
- [Schnellstart: Erster Stream](/docs/de/getting-started/quickstart.md)

## Verwandte Seiten

- [Architektur](/docs/de/developer-guide/architecture.md)
- [Glossar](/docs/de/reference/glossary.md)

---
_Stand: 2026-06-24 · Status: Stabil_

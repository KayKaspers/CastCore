---
title: "Plattformen"
description: "Ausgabeziele und Plattformen (Twitch, YouTube, RTMP) verwalten."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Plattformen

> Ein **Ziel (Destination)** beschreibt, **wohin** ein Stream gesendet wird – eine
> Plattform (Twitch/YouTube/Kick/…), ein eigener RTMP-Server, ein HLS-/Preview-Ausgang
> oder eine lokale Aufnahme.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Resources** bzw. im Stream-Job.

## Felder einer Destination

| Feld | Bedeutung |
| --- | --- |
| **Name** | Anzeigename. |
| **Kind** | `platform`, `rtmp`, `hls`, `recording`, `preview`. |
| **URL** | Ingest-/Ausgabe-URL (z. B. `rtmp://…/app`). |
| **Stream-Key** | Geheimer Schlüssel – verschlüsselt gespeichert, **write-only**. |

Bei `platform`/`rtmp` wird der Stream-Key beim Start sicher an die URL angehängt.

## Trennung von Transport und Metadaten

CastCore trennt bewusst:

- **FFmpeg / Destination** = Transport (URL + Stream-Key).
- **[Plattform-Metadaten](/docs/de/user-guide/metadata-thumbnails.md)** = Titel,
  Beschreibung, Kategorie, Tags, Thumbnail.

## Schritt für Schritt

1. Unter **Resources** eine Destination anlegen (Name, Kind, URL, optional Stream-Key).
2. Die Destination im [Stream-Editor](/docs/de/user-guide/stream-editor.md) einem Output
   zuweisen.
3. Optional pro Plattform [Metadaten](/docs/de/user-guide/metadata-thumbnails.md) pflegen.

## Hinweise

> 🔐 Stream-Keys werden verschlüsselt abgelegt und in Vorschauen/Logs **maskiert**.
> Nach außen ist nur sichtbar, *ob* ein Key gesetzt ist.

## Bei Problemen

- [Plattform-Fehler](/docs/de/troubleshooting/platform-errors.md) (RTMP rejected, falscher Key)

## Verwandte Seiten

- [Metadaten & Thumbnails](/docs/de/user-guide/metadata-thumbnails.md)
- [Stream-Editor](/docs/de/user-guide/stream-editor.md)

---
_Stand: 2026-06-24 · Status: Stabil_

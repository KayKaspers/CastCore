---
title: "Plattform-Fehler"
description: "RTMP rejected, falscher Stream-Key, API-Fehler."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Plattform-Fehler

> Wenn der Stream-Transport zu einer Plattform (Twitch/YouTube/…) scheitert.

**Zielgruppe:** Operatoren / Administratoren.

## Symptom: „RTMP rejected" / Verbindung abgewiesen

**Mögliche Ursachen:** falscher **Stream-Key**, falsche Ingest-**URL**, Konto nicht
streambereit, Stream bereits aktiv.
**Diagnose:** Live-Logs ansehen (RTMP-Fehlerzeile); Ziel-URL und Key in der
[Destination](/docs/de/user-guide/platforms.md) prüfen.
**Lösung:** Stream-Key neu aus dem Plattform-Dashboard kopieren; URL korrekt setzen
(z. B. `rtmp://…/app`). Der Key wird verschlüsselt gespeichert – einfach neu eingeben.

## Symptom: kein Bild / kein Ton auf der Plattform

**Ursachen:** Eingabe hat keinen Video-/Audiostream; Codec nicht plattformkompatibel.
**Lösung:** [Preflight](/docs/de/user-guide/preflight-checks.md) ausführen; ein
Re-Encode-Profil (`libx264`/`aac`) statt `copy` verwenden
([FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)).

## Symptom: falscher Stream-Key

Der Hinweis im Live-Log deutet darauf hin. Key in der Destination ersetzen.

## Symptom: Metadaten/Thumbnail nicht gesetzt

Transport (FFmpeg) und Metadaten sind getrennt. Titel/Beschreibung/Thumbnail unter
**Meta** pro Plattform pflegen ([Metadaten & Thumbnails](/docs/de/user-guide/metadata-thumbnails.md)).

## Relevante Logs

```bash
docker compose logs -f process-manager
```
Im UI: **Stream-Jobs → Live-Logs**.

## Verwandte Seiten

- [Plattformen](/docs/de/user-guide/platforms.md)
- [Metadaten & Thumbnails](/docs/de/user-guide/metadata-thumbnails.md)

---
_Stand: 2026-06-24 · Status: Stabil_

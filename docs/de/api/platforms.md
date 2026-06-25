---
title: "API: Plattformen & Metadaten"
description: "Destinations und Plattform-Metadaten/Templates."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Plattformen & Metadaten

> Ausgabeziele (Transport) und Plattform-Metadaten (Titel/Beschreibung/Thumbnail) sind
> getrennt. Operator+.

**Zielgruppe:** Entwickler / Integratoren.

## Ziele (Destinations)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/destinations[/{id}]` | Ziele; `kind` ∈ platform/rtmp/hls/recording/preview |

`stream_key` ist write-only und wird verschlüsselt gespeichert; Antworten zeigen nur
`has_stream_key`.

## Metadaten & Templates

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET` | `/api/v1/stream-jobs/{id}/metadata` | Alle Plattform-Metadaten eines Jobs |
| `PUT/DELETE` | `/api/v1/stream-jobs/{id}/metadata/{platform}` | Anlegen/aktualisieren/löschen |
| `GET` | `/api/v1/stream-jobs/{id}/metadata/{platform}/resolved` | Aufgelöste Metadaten + Warnungen |
| `GET` | `/api/v1/metadata/placeholders` | Liste der Platzhalter |
| `POST` | `/api/v1/metadata/resolve` | `{template, context}` → aufgelöster Text |

## Thumbnails / Assets

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/POST/DELETE` | `/api/v1/assets[/{id}]` | Bilder hochladen/auflisten/löschen |
| `GET` | `/api/v1/assets/{id}/file` | Bilddatei ausliefern |

Upload-Validierung (Magic-Bytes, Größe) – siehe
[Metadaten & Thumbnails](/docs/de/user-guide/metadata-thumbnails.md).

## Platzhalter

`{stream_title} {date} {time} {platform} {category} {tags} {source_name} {server_name} {channel_name}`
([Referenz](/docs/de/reference/placeholders.md)).

## Verwandte Seiten

- [Plattformen (UI)](/docs/de/user-guide/platforms.md)

---
_Stand: 2026-06-24 · Status: Stabil_

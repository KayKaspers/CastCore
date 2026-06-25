---
title: "API: Streams"
description: "Stream-Jobs, Profile, Start/Stop, Preflight."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Streams

> Stream-Jobs, FFmpeg-Profile, Ziele und Prozesssteuerung. Alle Routen erfordern
> mindestens **Operator**.

**Zielgruppe:** Entwickler / Integratoren.

## Stream-Jobs

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/POST` | `/api/v1/stream-jobs` | Auflisten / anlegen (mit Inputs/Outputs) |
| `GET/DELETE` | `/api/v1/stream-jobs/{id}` | Detail / löschen |
| `POST` | `/api/v1/stream-jobs/{id}/preview` | Maskierte Command-Vorschau |
| `POST` | `/api/v1/stream-jobs/{id}/preflight` | Startklar-Prüfung (🟢/🟡/🔴) |
| `POST` | `/api/v1/stream-jobs/{id}/dry-run` | Kurzer Test-Encode (Speed/FPS) |
| `POST` | `/api/v1/stream-jobs/{id}/start` · `/stop` · `/restart` | Prozesssteuerung |
| `POST` | `/api/v1/stream-jobs/{id}/recording` | Recording an/aus |

## Profile & Ziele

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/POST/PATCH/DELETE` | `/api/v1/ffmpeg-profiles[/{id}]` | FFmpeg-Profile |
| `GET/POST/PATCH/DELETE` | `/api/v1/destinations[/{id}]` | Ziele (Stream-Key write-only) |
| `POST` | `/api/v1/ffmpeg/preview` | Command aus Inputs/Outputs (maskiert) |

## Metadaten (pro Job/Plattform)

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `GET/PUT/DELETE` | `/api/v1/stream-jobs/{id}/metadata/{platform}` | Metadaten je Plattform |
| `GET` | `/api/v1/stream-jobs/{id}/metadata/{platform}/resolved` | Aufgelöste Vorschau |
| `POST` | `/api/v1/metadata/resolve` | Template generisch auflösen |

## Live-Logs

`WS /api/v1/ws/logs/{job_id}?token=<access>` – siehe [Monitoring](/docs/de/api/monitoring.md).

## Verwandte Seiten

- [Stream-Jobs (UI)](/docs/de/user-guide/streams.md) · [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)

---
_Stand: 2026-06-24 · Status: Stabil_

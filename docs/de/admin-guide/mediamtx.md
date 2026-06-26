---
title: "MediaMTX-Integration"
description: "Optionalen Media-Router (RTMP/SRT/WebRTC) anbinden und Ingest live überwachen."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-25
---

# MediaMTX-Integration

> **MediaMTX** ist ein optionaler Media-Router, der gängige Protokolle annimmt und
> weiterleitet (RTSP, RTMP, SRT, WebRTC, HLS). CastCore bleibt die **Steuerebene** und
> liest den Ingest-Status read-only über die MediaMTX-API.

**Zielgruppe:** Administratoren.

## Rollenverteilung

- **MediaMTX**: nimmt eingehende Streams an und routet/proxyt Protokolle.
- **FFmpeg** (über CastCore): transkodiert und verteilt an die Ziele.
- **CastCore**: Steuerung, Monitoring, Konfiguration.

## Aktivieren

1. In der `.env`:
   ```ini
   MEDIAMTX_ENABLED=true
   MEDIAMTX_API_URL=http://mediamtx:9997
   ```
2. Den Dienst über das Compose-Profil starten:
   ```bash
   docker compose --profile mediamtx up -d
   ```
3. Im **Monitoring** (`/monitoring`) erscheint das Panel **Ingest (MediaMTX)** mit
   Erreichbarkeit und aktiven Ingest-Pfaden.

## Ingest-Status

Das Panel zeigt pro Pfad: **Status** (Live/Bereit), **Quelle** (z. B. `rtmpConn`,
`srtConn`), **Tracks**, **empfangene Daten** und **Anzahl Leser**. Ohne aktive Publisher
ist die Liste leer – das ist normal.

## Ports

| Protokoll | Standard-Port |
| --- | --- |
| RTMP | 1935 |
| RTSP | 8554 |
| SRT | 8890/UDP |
| WebRTC | 8889 (HTTP), 8189/UDP (ICE) |
| HLS | 8888 |
| API | 9997 (nur intern) |

Veröffentliche nur die Protokoll-Ports, die du wirklich brauchst, am Host bzw. Reverse Proxy.

## Sicherheit

> 🔐 Die **API/Metrics-Ports** von MediaMTX sind nur im internen Docker-Netz `castcore`
> erreichbar und werden **nicht** am Host veröffentlicht – nur die Steuerebene fragt sie ab.
> Wenn du MediaMTX über den Host hinaus exponierst, richte echte Benutzer/Passwörter in
> `deploy/mediamtx/mediamtx.yml` ein (Abschnitt `authInternalUsers`) und beschränke
> `publish`/`read` entsprechend.

## Fehlerbehebung

- **Panel zeigt „Nicht erreichbar"**: Läuft der Container (`docker compose --profile mediamtx ps`)?
  Stimmt `MEDIAMTX_API_URL`? Sind beide Dienste im selben Netz `castcore`?
- **401 von der API**: Der API-Benutzer braucht die Aktionen `api`/`metrics` in
  `authInternalUsers` (in der mitgelieferten Konfiguration bereits gesetzt).

## Verwandte Seiten

- [Monitoring](/docs/de/user-guide/monitoring.md)
- [Deployment](/docs/de/admin-guide/deployment.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-25 · Status: Stabil_

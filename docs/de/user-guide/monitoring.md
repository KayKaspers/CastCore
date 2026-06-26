---
title: "Monitoring"
description: "System- und Stream-Metriken live: CPU, RAM, FPS, Bitrate."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-26
---

# Monitoring

> Das Monitoring zeigt System- und Stream-Metriken in Echtzeit. Es aktualisiert sich
> automatisch alle 2 Sekunden.

**Zielgruppe:** Anwender / Operatoren / Viewer. UI-Bereich: **Monitoring** (`/monitoring`).

## System-Kennzahlen

| Kachel | Bedeutung |
| --- | --- |
| **CPU** | Gesamt-CPU-Auslastung des Hosts. |
| **RAM** | Speicherauslastung (genutzt/gesamt). |
| **Disk** | Belegung des Datenverzeichnisses, freier Platz. |
| **FFmpeg** | Anzahl laufender FFmpeg-Prozesse. |

## Output-Tabelle

Pro aktivem Output: **Status**, **FPS**, **kbit/s**, **Speed**, **CPU%**, **RAM**.
Die Werte stammen aus dem Process Manager (psutil + FFmpeg-Progress) und werden in der
Datenbank abgeglichen.

## Stream-Health-Score

Im **Dashboard** zeigt das Panel **Stream-Health** pro Stream-Job einen Score **0–100** mit
Ampelstatus: 🟢 gesund · 🟡 Warnung · 🔴 kritisch · ⚪ unbekannt (läuft nicht).

Klick auf einen Job öffnet den **Diagnose-Assistenten**: statt nur „Score rot" zeigt er
**strukturierte Diagnosen** – mit Schweregrad, kurzer Erklärung, ausklappbarer technischer
Ursache, **empfohlenen Schritten** und Link zur passenden Doku (z. B. „Encoding zu langsam →
Auflösung/Preset/Bitrate senken, Hardware-Encoding prüfen"). Quellen: Health-Reasons,
FFmpeg-Version, Prozessstatus und – sofern zuvor ausgeführt – **gecachte** Preflight-/
Readiness-Ergebnisse (mit Zeitstempel; ältere als „veraltet" markiert).
API: `GET /api/v1/monitoring/jobs/{id}/diagnostics`. Es werden **keine** Secrets ausgegeben.

Der Score wird aus den **Live-Prozessmetriken** (Status, Speed, Reconnects, Dropped Frames,
FPS/Bitrate) je Output berechnet; der **schwächste laufende Output** bestimmt den Job-Score.
API: `GET /api/v1/monitoring/jobs/{id}/health` und `GET /api/v1/monitoring/health` (Übersicht).
Es werden **keine** Stream-Keys oder Secrets ausgegeben.

> ℹ️ Preflight- und Readiness-Ergebnisse fließen optional ein, werden für den Live-Score aber
> nicht bei jedem Abruf neu erhoben (das wäre zu teuer/rate-limitiert) – sie sind separat über
> Preflight bzw. **Verbindung testen** abrufbar.

## Wichtige Signale

> ⚠️ **Speed < 1.0×** (gelb markiert) bedeutet, dass die Echtzeit nicht gehalten wird –
> typisch bei zu hoher Last. Siehe [Performance](/docs/de/troubleshooting/performance.md).

## Hinweise

> 💡 FPS/Bitrate erscheinen erst, sobald FFmpeg Fortschrittszeilen liefert; CPU/RAM nach
> wenigen Sekunden Prozesslaufzeit.

## Ingest (MediaMTX)

Ist die optionale **MediaMTX**-Integration aktiviert, erscheint unter der Output-Tabelle
ein Panel **Ingest (MediaMTX)**. Es zeigt die Erreichbarkeit des Routers und alle aktiven
Ingest-Pfade (Pfadname, Live/Bereit, Quelle, Tracks, empfangene Daten, Leser). Einrichtung:
[MediaMTX-Integration](/docs/de/admin-guide/mediamtx.md).

## Prometheus / Grafana

CastCore stellt einen **Prometheus-Exporter** unter `/api/v1/metrics` bereit
(Standard-Textformat). Metriken u. a.: `castcore_cpu_percent`, `castcore_mem_percent`,
`castcore_disk_free_bytes`, `castcore_ffmpeg_processes`, `castcore_outputs_running` sowie
pro Output `castcore_output_fps|bitrate_kbps|speed|cpu_percent|rss_mb` (Label `output_id`).

Ein vorkonfigurierter Prometheus-Dienst liegt im Compose-Profil **monitoring**:

```bash
docker compose --profile monitoring up -d
```

> ⚠️ Der `/metrics`-Endpoint ist **ohne Auth** (Prometheus-Konvention). Labels enthalten
> nur UUIDs (keine Job-Namen). In Produktion am Reverse Proxy einschränken.

## Verwandte Seiten

- [Stream-Jobs](/docs/de/user-guide/streams.md)
- [Performance](/docs/de/troubleshooting/performance.md)
- [API: Monitoring](/docs/de/api/monitoring.md)
- [MediaMTX-Integration](/docs/de/admin-guide/mediamtx.md)

---
_Stand: 2026-06-26 · Status: Stabil_

---
title: "Monitoring"
description: "System- und Stream-Metriken live: CPU, RAM, FPS, Bitrate."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
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

## Wichtige Signale

> ⚠️ **Speed < 1.0×** (gelb markiert) bedeutet, dass die Echtzeit nicht gehalten wird –
> typisch bei zu hoher Last. Siehe [Performance](/docs/de/troubleshooting/performance.md).

## Hinweise

> 💡 FPS/Bitrate erscheinen erst, sobald FFmpeg Fortschrittszeilen liefert; CPU/RAM nach
> wenigen Sekunden Prozesslaufzeit.

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

---
_Stand: 2026-06-24 · Status: Stabil_

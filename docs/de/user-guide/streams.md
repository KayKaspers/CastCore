---
title: "Stream-Jobs"
description: "Stream-Jobs anlegen, starten, stoppen und überwachen."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Stream-Jobs

> Ein **Stream-Job** verbindet eine oder mehrere Quellen (Inputs) mit einem oder mehreren
> Zielen (Outputs) und wird über FFmpeg gesteuert.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Stream-Jobs** (`/streams`).

## Was macht diese Seite?

Die Liste zeigt alle Stream-Jobs mit **Status-Badge** und Aktionen. Von hier startest,
stoppst und überwachst du Streams.

## Aktionen je Job

| Aktion | Wirkung |
| --- | --- |
| **Start** | Baut das FFmpeg-Kommando und startet den/die Prozess(e). |
| **Stop** | Beendet die laufenden Prozesse sauber. |
| **Restart** | Stop + Start (z. B. nach Profiländerung). |
| **Live-Logs** | FFmpeg-Ausgabe in Echtzeit inkl. Klartext-Hinweisen. |
| **Meta** | [Plattform-Metadaten](/docs/de/user-guide/metadata-thumbnails.md) pflegen. |
| **Preflight** | [Startklar-Prüfung](/docs/de/user-guide/preflight-checks.md) (🟢/🟡/🔴). |
| **⌘ (Vorschau)** | Maskierte FFmpeg-Command-Vorschau (Stream-Keys verborgen). |
| **✕** | Job löschen. |

## Status-Werte

- `stopped` – nicht aktiv
- `starting` – wird gestartet
- `running` – läuft
- `failed` – Prozess fehlgeschlagen (siehe Logs)

Der Status wird **automatisch** aus dem echten Prozesszustand abgeglichen.

## Schritt für Schritt: Job starten

1. Job in der Liste auswählen (oder neu anlegen → [Stream-Editor](/docs/de/user-guide/stream-editor.md)).
2. **Preflight** ausführen – bei Grün/Gelb fortfahren.
3. **Start** klicken, **Live-Logs** öffnen und Verlauf beobachten.

## Hinweise

> 💡 Bei Multi-Output wird **pro aktivem Output ein FFmpeg-Prozess** überwacht.

> 🔐 Stream-Keys sind in der Command-Vorschau und in Logs **maskiert**.

## Bei Problemen

- [Stream startet nicht](/docs/de/troubleshooting/stream-not-starting.md)
- [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md)

## Verwandte Seiten

- [Stream-Editor](/docs/de/user-guide/stream-editor.md)
- [Monitoring](/docs/de/user-guide/monitoring.md)
- [Recordings & Replay](/docs/de/user-guide/recordings-replay.md)

---
_Stand: 2026-06-24 · Status: Stabil_

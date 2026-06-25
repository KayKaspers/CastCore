---
title: "Recordings & Replay"
description: "Streams aufnehmen, Aufnahmen verwalten und herunterladen."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Recordings & Replay

> CastCore kann jeden Stream parallel als MP4 aufnehmen. Aufnahmen erscheinen mit Dauer,
> Größe und Status im Replay-Bereich.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Recordings / Replay** (`/recordings`).

## Aufnahme aktivieren

1. Im [Stream-Editor](/docs/de/user-guide/stream-editor.md) die Option **Recording**
   aktivieren (oder am bestehenden Job umschalten).
2. Job **starten** – parallel zu den Live-Outputs entsteht eine Aufnahme mit
   Zeitstempel-Dateinamen unter dem Recordings-Verzeichnis.
3. Beim **Stop** wird die Aufnahme finalisiert (Größe, Dauer, Status `completed`).

## Replay-Liste

| Spalte | Bedeutung |
| --- | --- |
| **Datei** | Zeitstempel-Dateiname + Startzeit. |
| **Status** | `recording` (läuft), `completed`, `failed`. |
| **Dauer / Größe** | Länge und Dateigröße. |
| **↓** | Download (erst nach Abschluss). |

## Aufbewahrung

Pro Job lässt sich eine **Aufbewahrungsdauer (Tage)** setzen. Das Feld `retention_until`
wird gespeichert; die automatische Bereinigung folgt über den
[Scheduler](/docs/de/user-guide/settings.md).

## Hinweise

> 💡 Aufnahmen liegen im `RECORDINGS_DIR` (siehe
> [Umgebungsvariablen](/docs/de/reference/environment-variables.md)).

## Verwandte Seiten

- [Stream-Editor](/docs/de/user-guide/stream-editor.md)
- [Backup & Restore](/docs/de/user-guide/backup-restore.md)

---
_Stand: 2026-06-24 · Status: Stabil_

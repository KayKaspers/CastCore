---
title: "Stream startet nicht"
description: "Diagnose, wenn ein Stream nicht startet."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Stream startet nicht

> Wenn ein Stream-Job auf „Start" nicht in den Zustand `running` wechselt.

**Zielgruppe:** Operatoren / Administratoren.

## Diagnose in 4 Schritten

1. **Preflight ausführen.** Rote Punkte zeigen die blockierende Ursache (Quelle
   unlesbar, kein Video, fehlende Output-URL/Stream-Key, kein Speicherplatz).
2. **Live-Logs öffnen.** Die erste rote Zeile + Hinweis-Banner nennt meist die Ursache.
3. **Command-Vorschau** (`⌘`) prüfen: Ist die Eingabe-URI korrekt? Fehlt ein Output?
4. **Process-Manager-Log** prüfen:
   ```bash
   docker compose logs -f process-manager
   ```

## Häufige Ursachen

| Ursache | Lösung |
| --- | --- |
| Kein aktiver Output | Im Stream-Editor mindestens einen Output aktivieren |
| Ziel ohne URL/Stream-Key | [Destination](/docs/de/user-guide/platforms.md) vervollständigen |
| Quelle nicht erreichbar | [Quelle testen/mounten](/docs/de/user-guide/sources-storage.md) |
| FFmpeg-Parameterfehler | [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md) |
| Redis nicht erreichbar (Steuerkanal) | [Docker-Probleme](/docs/de/troubleshooting/docker.md) |

## Hintergrund

Der Start läuft so: **Backend → Redis (`castcore:control`) → Process Manager → FFmpeg**.
Bleibt der Status auf `starting`, prüfe, ob `process-manager` und `redis` laufen
(`docker compose ps`).

## Verwandte Seiten

- [Preflight-Checks](/docs/de/user-guide/preflight-checks.md)
- [Process Manager](/docs/de/developer-guide/process-manager.md)

---
_Stand: 2026-06-24 · Status: Stabil_

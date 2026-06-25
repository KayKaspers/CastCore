---
title: "Troubleshooting"
description: "Einstieg in die Fehlersuche nach Symptom."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Troubleshooting

> Finde dein Symptom und folge dem Link. Jede Seite ist nach **Symptom → Mögliche
> Ursachen → Diagnose → Lösung → Relevante Logs** aufgebaut.

## Nach Symptom

| Symptom | Seite |
| --- | --- |
| FFmpeg startet nicht / nicht gefunden | [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md) |
| Stream startet nicht | [Stream startet nicht](/docs/de/troubleshooting/stream-not-starting.md) |
| Kein Bild / kein Ton / RTMP rejected / falscher Stream-Key | [Plattform-Fehler](/docs/de/troubleshooting/platform-errors.md) |
| SMB-Mount schlägt fehl | [SMB-Probleme](/docs/de/troubleshooting/smb-problems.md) |
| Encoding-Speed < 1.0x, hohe CPU | [Performance](/docs/de/troubleshooting/performance.md) |
| Container starten nicht, DB/Redis nicht erreichbar | [Docker-Probleme](/docs/de/troubleshooting/docker.md) |
| Probleme bei nativer Installation | [Native Installation](/docs/de/troubleshooting/native-installation.md) |

## Allgemeine Erstdiagnose

1. **Live-Logs** des betroffenen Stream-Jobs öffnen – CastCore zeigt zusätzlich
   verständliche Klartext-Hinweise (Stream-Health-Assistant).
2. **Preflight-Check** ausführen – er prüft Quelle, Video/Audio, Output-URL, Stream-Key,
   Speicherplatz.
3. **Service-Logs** ansehen:
   ```bash
   docker compose logs -f backend process-manager
   ```

## Verwandte Seiten

- [Logs](/docs/de/admin-guide/logs.md)
- [Monitoring](/docs/de/user-guide/monitoring.md)

---
_Stand: 2026-06-24 · Status: Stabil_

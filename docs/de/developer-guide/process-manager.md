---
title: "Process Manager"
description: "Supervidierung langlaufender FFmpeg-Prozesse."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Process Manager

> Eigener Dienst (`process_manager/`), der die langlaufenden FFmpeg-Streamprozesse
> startet, überwacht und stoppt.

**Zielgruppe:** Entwickler.

## Funktionsweise

1. Abonniert den Redis-Kanal **`castcore:control`** und empfängt
   `{action: start|stop|restart, output_id, job_id, argv}`.
2. Spawnt FFmpeg per `asyncio.create_subprocess_exec(*argv)` (**shell-frei**) –
   ein Prozess pro aktivem Output.
3. Pumpt stderr/stdout **zeilenweise** nach **`castcore:logs:<job_id>`**, parst
   Progress (fps/bitrate/speed) und sampelt CPU/RSS via psutil → **`castcore:status`**.
4. Erkennt Failure-Muster und hängt einen übersetzbaren **Hint**-Code an (Health-Assistant).

## Zusammenspiel mit dem Backend

Der **Status-Consumer** im Backend liest `castcore:status`, schreibt `process_status`,
gleicht Job-/Channel-Status ab, feuert Benachrichtigungen und steuert die
[Selbstheilung](/docs/de/user-guide/streams.md).

## Channels & Recordings

Channels nutzen den FFmpeg concat-Demuxer (Loop → HLS); Recordings sind synthetische
mp4-Outputs. Beide werden über denselben Steuerkanal supervidiert.

## Verwandte Seiten

- [FFmpeg Command Builder](/docs/de/developer-guide/ffmpeg-command-builder.md)
- [WebSockets / SSE](/docs/de/developer-guide/websocket-sse.md)
- [Architektur](/docs/de/developer-guide/architecture.md)

---
_Stand: 2026-06-24 · Status: Stabil_

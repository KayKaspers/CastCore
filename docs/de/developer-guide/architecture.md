---
title: "Architektur"
description: "Zielarchitektur, Komponenten und Datenfluss von CastCore."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Architektur

> Überblick über die Komponenten und den Datenfluss. Die ausführliche Fassung steht in
> [`docs/ARCHITECTURE.md`](https://github.com/KayKaspers/CastCore/blob/main/docs/ARCHITECTURE.md).

**Zielgruppe:** Entwickler.

## Komponenten

- **Frontend** – React/Vite-SPA (Nginx), spricht die REST-API + WebSockets.
- **Backend** – FastAPI: API, Auth, Hintergrund-Loops (Status-Consumer, Scheduler).
- **Process Manager** – supervidiert langlaufende FFmpeg-Prozesse.
- **Worker** – arq: kurze Async-Jobs (Scan, ffprobe, Thumbnails, Backups).
- **PostgreSQL** – Soll-Zustand/Datenmodell. **Redis** – Cache, Queue, **Steuer-/Status-Bus**.

## Kern-Entscheidung: Prozesssteuerung über Redis

Streams sind **langlaufende, überwachte Prozesse**, keine Queue-Tasks. Ablauf:

```
Backend → Redis (castcore:control) → Process Manager → FFmpeg
FFmpeg → Process Manager → Redis (castcore:status / :logs:<job>) → Backend → WebSocket → UI
```

Der **Status-Consumer** im Backend gleicht den DB-Zustand mit dem echten Prozesszustand
ab (Job-/Channel-Status, `process_status`), feuert Benachrichtigungen und steuert die
[Selbstheilung](/docs/de/user-guide/streams.md).

## Sicherheit by design

Argon2-Passwörter, JWT mit Rotation, RBAC, Fernet-verschlüsselte Secrets, **kein
Shell-Aufruf** (argv-Listen), Path-Traversal-Schutz, sichere Uploads. Siehe
[Security](/docs/de/admin-guide/security.md).

## Verwandte Seiten

- [Projektstruktur](/docs/de/developer-guide/project-structure.md)
- [Process Manager](/docs/de/developer-guide/process-manager.md)
- [FFmpeg Command Builder](/docs/de/developer-guide/ffmpeg-command-builder.md)

---
_Stand: 2026-06-24 · Status: Stabil_

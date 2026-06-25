---
title: "Architecture"
description: "Target architecture, components and data flow of CastCore."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Architecture

> Overview of components and data flow. The detailed version is in
> [`docs/ARCHITECTURE.md`](https://github.com/KayKaspers/CastCore/blob/main/docs/ARCHITECTURE.md).

**Audience:** developers.

## Components

- **Frontend** – React/Vite SPA (Nginx), talks to the REST API + WebSockets.
- **Backend** – FastAPI: API, auth, background loops (status consumer, scheduler).
- **Process Manager** – supervises long-running FFmpeg processes.
- **Worker** – arq: short async jobs (scan, ffprobe, thumbnails, backups).
- **PostgreSQL** – desired state / data model. **Redis** – cache, queue, **control/status bus**.

## Key decision: process control via Redis

Streams are **long-running supervised processes**, not queue tasks. Flow:

```
Backend → Redis (castcore:control) → Process Manager → FFmpeg
FFmpeg → Process Manager → Redis (castcore:status / :logs:<job>) → Backend → WebSocket → UI
```

The backend **status consumer** reconciles DB state with the real process state
(job/channel status, `process_status`), fires notifications and drives
[self-healing](/docs/en/user-guide/streams.md).

## Security by design

argon2 passwords, JWT with rotation, RBAC, Fernet-encrypted secrets, **no shell**
(argv lists), path-traversal protection, safe uploads. See
[Security](/docs/en/admin-guide/security.md).

## Related pages

- [Project structure](/docs/en/developer-guide/project-structure.md)
- [Process manager](/docs/en/developer-guide/process-manager.md)
- [FFmpeg command builder](/docs/en/developer-guide/ffmpeg-command-builder.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

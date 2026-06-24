# CastCore — Architecture

> CastCore — **Stream. Manage. Control.** · Self-Hosted Streaming Operations Suite

This document is the canonical concept: goal, assumptions, product strategy, tech
stack, target architecture, deployment, modules, and the cross-cutting concepts.
Detailed companions: [DATA_MODEL](DATA_MODEL.md), [API](API.md),
[DEPLOYMENT](DEPLOYMENT.md), [SECURITY](SECURITY.md), [ROADMAP](ROADMAP.md).

---

## 1. Goal

CastCore is a **streaming operations suite**, not an FFmpeg web wrapper. It is a
control plane that manages the full lifecycle of streaming: sources, media analysis,
stream planning, safe FFmpeg supervision, multi-destination output, monitoring,
recording, linear channels, scheduling and deployment.

It must install on a **fresh Linux system** (Debian 12 / Ubuntu LTS, VM, LXC, bare
metal, Proxmox) where nothing but the OS exists, and bring or install every component
it needs — via Docker Compose **or** native install scripts.

The product test: an operator should manage sources, plan and supervise streams,
push to multiple platforms with per-target metadata, run 24/7 channels, record and
replay, and **understand failures in plain language** — all from one UI.

## 2. Assumptions

- **Single-node first.** Phase 1–3 target one host. Clustering/multi-worker is Phase 4.
- **Linux runtime target**, even though development happens on Windows. FFmpeg,
  mounts and systemd integration assume Linux; Docker is the portable path.
- **FFmpeg streams are long-running supervised processes**, not queue tasks. This
  drives a dedicated *Process Manager* service separate from the async worker.
- **Operators are technical but not all FFmpeg experts.** The UI shows the real
  command and real logs *and* plain-language explanations.
- **Secrets are first-class.** Stream keys, SMB/OAuth credentials are encrypted at
  rest, masked in UI, never logged. Encryption key comes from the environment.
- **Mounts (SMB/NFS/rclone) are easier and safer on the host** than inside
  containers; CastCore supports both but documents and defaults to host-side mounts.
- **Network is untrusted/unstable** for cloud sources and platform APIs; everything
  that touches the network must time out, retry and report status.
- Bilingual **DE/EN** is a hard requirement, not an afterthought.

## 3. Comparison-based product strategy

| Project | What it's strong at | What CastCore takes |
| --- | --- | --- |
| **datarhei Restreamer** | Simple self-hosted streaming, clean FFmpeg/API layer | "Stream in a few clicks" UX, live status (uptime/bitrate/FPS/health), publication-services model for outputs |
| **Owncast** | Self-hosted livestreaming with watchpage + chat | Optional internal watchpage / webplayer / (later) chat — serve own private streams, not only relay |
| **MediaMTX** | Media router & protocol gateway (RTSP/RTMP/SRT/WebRTC/HLS) | Integrate it, don't compete. CastCore = control plane, MediaMTX = routing, FFmpeg = transcoding |
| **Ant Media** | WebRTC, low-latency, LL-HLS | Latency profiles (standard / low / ultra-low) prepared; latency as a monitoring metric |
| **ErsatzTV** | Linear channels from libraries, schedules, EPG, M3U | Channel Mode: 24/7 channels, playlists, schedules, repeats, fallback, XMLTV/EPG, M3U export |
| **CasparCG** | Pro graphics/playout | Later: overlays, lower-thirds, scenes, branding insertions |
| **Open Streaming Platform** | Recording + on-demand | Recording, replay/VoD archive, landing pages, highlight clips |
| **Tdarr / FileFlows / Unmanic** | Automated transcoding, rule-based optimization | Preflight ffprobe analysis, "not streaming-friendly" hints, optional transcoding queue, proxy files |

**Differentiator:** CastCore unifies *source/storage management + media analysis +
safe FFmpeg control + multi-output + platform metadata + channels + recording +
monitoring + plain-language health* behind one authenticated, bilingual, easy-to-install
control plane. None of the above does all of this together.

## 4. Recommended tech stack — **Option A (Python / FastAPI)**

**Decision: Option A.** Reasoning against the weighted criteria:

| Criterion | Python/FastAPI (A) | Node/NestJS (B) | Winner |
| --- | --- | --- | --- |
| FFmpeg process mgmt | `asyncio` subprocess, `psutil` for CPU/RAM/handles, mature signal handling | `child_process`, fine but less batteries-included for process introspection | A |
| ffprobe / media analysis | JSON parsing trivial; rich data tooling | Equivalent | tie |
| Linux integration (mounts, systemd) | Ops/glue scripting is Python's home turf | Workable | A |
| SMB/NFS/rclone | `smbprotocol`, `subprocess` to `mount`/`rclone`; strong | Equivalent via subprocess | tie |
| Worker model | arq/Celery/RQ mature | BullMQ mature | tie |
| WebSockets / SSE | FastAPI native, Starlette | NestJS gateways | tie |
| Type-safety end-to-end | Pydantic v2 (not shared with TS frontend) | Shared TS types possible | B |
| Maintainability | Small surface, explicit | DI framework heavier | A |
| Security primitives | argon2, cryptography (Fernet), well-trodden | Equivalent | tie |
| Deployment footprint | Single slim image, few deps | Similar | tie |

Python wins the categories that dominate this domain (process supervision, OS/media
integration, ops scripting). The one Node advantage — shared types with a TS frontend —
is mitigated by generating a **typed OpenAPI client** for the frontend from FastAPI.

**Stack:**

- **Backend/API:** Python 3.12, **FastAPI**, **SQLAlchemy 2.0 (async)** + **Alembic**,
  **Pydantic v2**, asyncpg.
- **Process Manager:** standalone asyncio service supervising FFmpeg subprocesses;
  state in Postgres, live logs/metrics on Redis pub/sub, control via Redis commands.
- **Worker:** **arq** (async, Redis-native) for media scan, ffprobe, thumbnails,
  backups, scheduled jobs.
- **DB:** PostgreSQL 16. **Cache/Queue/PubSub:** Redis 7.
- **Frontend:** React 18 + TypeScript + **Vite**, **TailwindCSS** (CastCore brand
  tokens), **i18next**, **TanStack Query**, **Zustand**, Radix-based components.
- **Reverse proxy:** Caddy (automatic HTTPS). **Optional:** MediaMTX.

## 5. Target architecture

```
                         ┌──────────────────────── Browser (DE/EN) ───────────────────────┐
                         │  React SPA · Tailwind(brand tokens) · i18next · TanStack Query  │
                         └───────────────▲───────────────────────────────▲─────────────────┘
                                         │ HTTPS (REST)                   │ WSS (live logs/status)
                              ┌──────────┴───────────────────────────────┴──────────┐
                              │                  Caddy (TLS, routing)                │
                              └──────────┬───────────────────────────────┬──────────┘
                                         │                               │
                              ┌──────────▼──────────┐         ┌──────────▼──────────┐
                              │   FastAPI Backend   │  REST   │   Static Frontend   │
                              │  Auth · API · WS    │         │      (built SPA)    │
                              └─┬───────┬────────┬──┘         └─────────────────────┘
                  SQLAlchemy    │       │        │  Redis pub/sub + commands
                       ┌────────▼──┐ ┌──▼─────┐  │
                       │PostgreSQL │ │ Redis  │◄─┼──────────────┬───────────────┐
                       └───────────┘ └────────┘  │              │               │
                                                 │              │               │
                                       ┌─────────▼────────┐ ┌───▼──────────┐ ┌──▼──────────┐
                                       │ Process Manager  │ │  arq Worker  │ │  Scheduler  │
                                       │ supervises FFmpeg│ │ scan/probe/  │ │ cron-like   │
                                       │ (1 proc / output)│ │ thumb/backup │ │ jobs+channels│
                                       └───┬─────────┬────┘ └──────────────┘ └─────────────┘
                                           │ spawn   │ stats(psutil)
                                     ┌─────▼───┐ ┌───▼────┐        ┌──────────────────────┐
                                     │ FFmpeg  │ │ ffprobe│        │ Optional: MediaMTX    │
                                     │ procs   │ │        │        │ RTSP/RTMP/SRT/WebRTC  │
                                     └─────────┘ └────────┘        └──────────────────────┘
                                           │
                  ┌────────────────────────┼─────────────────────────────┐
            local files / watch     mounts (SMB/NFS/SFTP/WebDAV)    cloud (rclone/S3)
```

**Key architectural decisions**

1. **Process Manager ≠ Worker.** Streams are supervised long-lived processes
   (start/stop/restart, reconnect, fallback, health). The worker handles bounded async
   jobs. Conflating them (e.g. one Celery worker) makes supervision and live logs fragile.
2. **Redis as the live bus.** FFmpeg stdout/stderr is parsed by the Process Manager and
   published to Redis channels; the backend subscribes and fans out to WebSocket
   clients. Process control (stop/restart) flows backend → Redis → Process Manager.
3. **DB is the source of truth for desired state**; the Process Manager reconciles
   actual process state toward it (a small control loop) — survives restarts.
4. **Safe FFmpeg only.** Commands are built as **argument lists** (never shell strings);
   see [FFmpeg Command Builder](#7-modules). Secrets masked in previews and logs.
5. **Typed client.** FastAPI emits OpenAPI; the frontend consumes a generated typed
   client, recovering most of the "shared types" benefit of a Node stack.

## 6. Deployment architecture

Two supported paths (full detail in [DEPLOYMENT.md](DEPLOYMENT.md)):

- **Docker-first** — `docker-compose.yml` with services: `frontend`, `backend`,
  `process-manager`, `worker`, `postgres`, `redis`, `caddy`, optional `mediamtx`
  (profile) and monitoring exporters (profile). Healthchecks, restart policies,
  named volumes, `.env.example`, backup/restore/upgrade docs, Caddy HTTPS.
- **Native** — `scripts/install.sh`, `update.sh`, `uninstall.sh`: OS check, package
  + FFmpeg/ffprobe install, PostgreSQL & Redis (local or external), dedicated system
  user `castcore`, systemd units (`castcore-backend`, `castcore-process-manager`,
  `castcore-worker`, `castcore-scheduler`), data/log dirs, restrictive permissions,
  optional reverse proxy + HTTPS.

## 7. Modules

Each module is a backend service package (`backend/app/services/<module>`) with an API
router (`backend/app/api/v1/endpoints/<module>.py`) where it is externally exposed.

**Mandatory:** Frontend · Backend/API · Auth · Users/Roles · Settings · Setup ·
**FFmpeg Command Builder** · **FFmpeg Process Manager** · Worker · Scheduler · Log ·
Monitoring · Stream-Health · Media-Library · Storage · Mount · Platform · Metadata ·
Thumbnail/Asset · Channel · Playlist · Recording · Backup/Restore · Update ·
Audit-Log · Notification · *(optional)* MediaMTX integration.

Highlight — **FFmpeg Command Builder** (security-critical): produces ordered argument
lists (global → input opts → input → filters → output opts → output), validates every
parameter, supports multi-input/multi-output, HLS/RTMP/SRT, stream-copy vs re-encode,
loop, reconnect, filter chains, expert params; renders a **masked preview**; fully
unit-tested. Never constructs a shell string.

Highlight — **Process Manager**: one supervised FFmpeg process per active output (or
per job for single-output), with reconnect/restart/fallback policy, health scoring
from parsed FFmpeg progress (fps, bitrate, speed, dropped frames) + psutil.

## 8. Data model

~40 entities across users/security, streaming, sources/storage, media, channels,
recording, ops. Full schema in [DATA_MODEL.md](DATA_MODEL.md). Core clusters:

- **Security:** users, roles, sessions, api_tokens, audit_events.
- **Streaming:** stream_jobs, stream_profiles, ffmpeg_profiles, inputs, outputs,
  destinations, process_status, health_checks, preflight_reports.
- **Platforms:** platforms, platform_accounts, platform_profiles, platform_metadata,
  thumbnails, assets.
- **Sources/Storage:** storage_sources (+ smb/nfs/cloud detail), mounts,
  media_library_items, media_probe_data.
- **Channels:** channels, channel_schedule, channel_programs, playlists, playlist_items.
- **Recording/replay:** recordings, replay_items.
- **Ops:** settings, setup_state, scheduler_entries, notifications, backups,
  update_state, logs.

## 9. API design

REST for CRUD; **WebSocket/SSE** for live logs and status. Versioned under `/api/v1`.
Translatable **error codes** (`error.preflight.source_unreachable`) instead of baked-in
English strings. Full surface in [API.md](API.md).

## 10. UI/UX

Dark-first admin design using the CastCore brand tokens (Deep Navy background, Core
Green / Signal Cyan accents, Inter). 21 mandatory pages (Login, Setup Wizard,
Dashboard, Stream Jobs, …, Updates). Required UX: DE/EN switcher, status badges, health
score, live logs, command preview, expert mode, form validation, help texts, warnings,
test buttons, secret masking, thumbnail/description/platform previews, plain-language
errors alongside technical logs. Full concept in this doc's UI section is mirrored into
component structure under `frontend/src/pages` and `frontend/src/components`.

## 11. Security

Login + roles (Admin/Operator/Viewer), argon2 password hashing, JWT access+refresh
with rotation, CSRF/XSS protection, rate limiting, audit logs, encrypted secret storage
(Fernet) for stream keys / API tokens / OAuth refresh tokens / SMB passwords, path
traversal & shell-injection prevention, safe uploads, restrictive file permissions,
optional 2FA (Phase 4). Detail in [SECURITY.md](SECURITY.md).

## 12. Storage / source concept

Three source classes behind one `StorageSource` abstraction:

- **Local:** files, folders, watch-folders, playlists, HLS/MPEG-TS, webcam, capture/HDMI.
- **Network:** SMB/CIFS, NFS, SFTP, FTP/FTPS, WebDAV, HTTP(S), RTSP, RTMP, HLS, SRT —
  with test, secure credentials, mount path, automount toggle, manual mount/unmount,
  status, read-only, periodic rescan, offline detection.
- **Cloud (modular):** Google Drive, Dropbox, OneDrive, S3-compatible, Nextcloud/WebDAV,
  Backblaze B2, Cloudflare R2, generic rclone remotes — test, OAuth/API secrets,
  browse remote, cache dir, sync vs mount, resilience for big files/unstable links.

**SMB** is a first-class form (display name, server, share, domain, user, secured
password, mount path, SMB version, read-only, automount, test). Host-mount vs
container-mount tradeoffs documented; credentials in restrictive cred files, never in
logs, no unsafe shell execution.

## 13. Platform / metadata concept

Clean separation: **FFmpeg = transport**, **Platform-Service = metadata/thumbnail/API/
status**. Platforms (Twitch/YouTube/Kick/Facebook/own RTMP/custom) carry per-platform &
per-stream metadata (title, description, category, tags, language, visibility,
thumbnail, scheduled start). **Description templates** support placeholders
(`{stream_title}`, `{date}`, `{time}`, `{platform}`, `{category}`, `{tags}`,
`{source_name}`, `{server_name}`, `{channel_name}`). Final resolved metadata is shown
and checked before stream start.

## 14. Preflight / health concept

**Preflight** runs before every start and returns 🟢/🟡/🔴: source reachable, file
present, mount/cloud available, ffprobe reads input, has video/(optional) audio,
profile complete, output URL & stream-key present, metadata complete, thumbnail valid,
disk/CPU/RAM sufficient, write permissions, recording path available, upload bandwidth
plausible, secrets present-but-hidden, no blocking config errors.

**Dry-Run/Teststream:** ~30s test encode, local/internal-HLS output, encoding-speed &
CPU/RAM estimate, FFmpeg error detection, profile validation, result report.

**Stream-Health Assistant:** parses FFmpeg logs/process data into plain-language hints
(input unreachable, audio/video missing, bitrate too low, speed < 1.0x, RTMP rejected,
likely wrong stream key, unstable network, SMB mount lost, cloud unreachable, disk full,
platform unreachable, FFmpeg crashed). Technical logs remain visible.

**Fallback/emergency:** fallback video/still/(optional) audio, auto-reconnect, auto
restart, max-retry, failure notifications, keep streaming on record failure, send
fallback on source loss, switch back on recovery.

## 15. Channel / recording concept

**Channel Mode** (linear): name, logo, description, source, playlist, schedule, repeat
rules, fallback, outputs, profile, platform metadata, optional EPG/recording. Features:
24/7, scheduled programs, playlists, shuffle/fixed order, repeats, fallback on missing
media, XMLTV/EPG export, M3U export, own HLS/RTMP output.

**Recording/Replay:** per-stream recording toggle, segmentation, filename templates,
storage location, retention rules, replay archive, VoD prep, highlight markers,
optional YouTube upload prep.

## 16. Project structure

See [`../README.md`](../README.md) and the repository tree. Top level: `frontend/`,
`backend/`, `worker/`, `process_manager/`, `shared/`, `deploy/`, `docs/`, `scripts/`,
`branding/`, plus `docker-compose.yml` and `.env.example`. Backend is organised into
`core/`, `api/`, `models/`, `schemas/`, `services/`, `i18n/`, `migrations/`.

## 17. Milestones

Four phases (Solid base → Streaming suite → Broadcast/channels → Advanced/pro). Full
breakdown in [ROADMAP.md](ROADMAP.md).

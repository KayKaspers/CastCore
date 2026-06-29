<p align="center">
  <img src="branding/svg/castcore-logo-horizontal-dark.svg" alt="CastCore" width="420">
</p>

<h1 align="center">CastCore</h1>
<p align="center"><strong>Stream. Manage. Control.</strong></p>
<p align="center">Self-Hosted Streaming Operations Suite</p>

---

CastCore is a self-hosted **streaming operations suite** — a control plane for FFmpeg
streams, media sources, network/cloud storage, platform metadata, multi-output
streaming, monitoring, recording and linear channels.

It is **not** "just an FFmpeg web wrapper". CastCore manages sources, analyses media,
plans streams, supervises FFmpeg processes safely, monitors outputs, explains failures
in plain language and offers automatic fallbacks.

> **Positioning:** CastCore is a self-hosted streaming-control suite for managing
> FFmpeg streams, media sources, network & cloud storage, platform metadata,
> multi-destination streaming, monitoring, recording and linear channels.

## Status

🟡 **Early beta / advanced alpha.** The core is built and runs on Docker; it is suitable for
self-hosted early use, **not yet production-hardened**. See [`CHANGELOG.md`](CHANGELOG.md) for
the authoritative, chronological record of what landed.

**Implemented (functional):** auth (JWT + rotating refresh, RBAC Admin/Operator/Viewer), 2FA
(TOTP), API tokens, session management, **rate limiting** on sensitive auth endpoints;
stream jobs with a shell-free FFmpeg command builder + multi-output, live logs (WebSocket/
Redis), auto-restart; monitoring + Prometheus exporter; a **stream health score + diagnostics
assistant**; **FFmpeg version detection & safe-media mode** (CVE-2026-8461 mitigation); local +
SMB/CIFS storage; media library,
playlists, channels (HLS/EPG), recording, scheduler, notifications, backup/restore; MediaMTX
ingest (status + as a source); platform OAuth (YouTube/Twitch) with **metadata push** and a
**readiness check**; a full
bilingual docs/help system; and CI for backend (ruff/mypy/pytest incl. API integration
tests), frontend (eslint/build), docs and compose, a **Docker FFmpeg build smoke test** (builds
all images with `FFMPEG_VARIANT=copy` and asserts ffmpeg/ffprobe ≥ 8.1.2), plus a manual
full-stack E2E workflow.

**Known gaps / not yet:**
- **GPU encoding** (NVENC/QSV/VAAPI) is not verified end-to-end — the bundled FFmpeg supports it,
  but it additionally needs host drivers + a GPU-enabled container runtime (see
  [FFmpeg requirements](docs/en/admin-guide/ffmpeg-requirements.md)).
- **OAuth metadata push** is implemented for YouTube/Twitch but **not yet verified against the
  live platform APIs** (CastCore-side logic is tested with mocked APIs; real push needs client
  credentials + a connected account).
- **Storage**: only local + SMB/CIFS; NFS/SFTP/WebDAV/rclone/cloud are not implemented.
- **Hardening**: worker runs non-root + `cap_drop`; backend/process-manager still run as root
  (only `no-new-privileges`). No **CSP** header yet.
- **Tests**: no frontend tests and no migration tests yet. The E2E workflow is **manual**
  (`workflow_dispatch`).
- Native `install.sh`/`update.sh`/`uninstall.sh` exist but are **not fully verified**.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the milestone plan.

## Tech stack

| Layer            | Choice                                                            |
| ---------------- | ----------------------------------------------------------------- |
| Backend / API    | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Pydantic v2        |
| Process manager  | Dedicated asyncio supervisor for long-running FFmpeg processes    |
| Worker           | arq (Redis) for scans, ffprobe, thumbnails, backups               |
| Database         | PostgreSQL 16                                                     |
| Cache / Queue / PubSub | Redis 7                                                     |
| Frontend         | React 18 · TypeScript · Vite · Tailwind · i18next · zustand (+ a custom data hook) |
| Reverse proxy    | Caddy (automatic HTTPS)                                           |
| Optional router  | MediaMTX (RTSP/RTMP/SRT/WebRTC/HLS routing)                       |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full rationale.

## Installation

> **Verified path:** Docker / Docker Compose is the recommended and tested deployment.
> The native install scripts exist but are **experimental / not fully verified** (see below).

### Prerequisites

- A Linux host (or Docker Desktop on Windows/macOS) with **Docker Engine 24+** and the
  **Docker Compose v2** plugin.
- ~2 GB RAM and a few GB of disk for the database, media and recordings.
- Outbound internet for the initial image build (pulls base images + packages).
- The bundled images run **Debian 13 (trixie)**; by default they ship a **pinned, static
  FFmpeg/ffprobe ≥ 8.1.2** (`FFMPEG_VARIANT=copy`, verified by a build-time version gate). The
  `apt` (Debian package) and `static` (custom tarball + SHA256) variants are documented fallbacks.
  See [FFmpeg requirements](docs/en/admin-guide/ffmpeg-requirements.md).

### 1. Configure (`.env`)

```bash
cp .env.example .env
```

Edit `.env` and set **at least**:

- `SECRET_KEY` — `openssl rand -hex 32`
- `ENCRYPTION_KEY` — a Fernet key:
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `POSTGRES_PASSWORD` — any strong value
- `DOMAIN` — `localhost` for local use, or your public hostname (Caddy gets a real cert via ACME)

`.env` is git-ignored — never commit it. Keep the `ENCRYPTION_KEY` safe and backed up
**separately**: without it, stored secrets (stream keys, platform tokens) cannot be decrypted.

### 2. Start

```bash
docker compose up -d
```

The backend auto-runs database migrations on start. Optional service profiles:

```bash
docker compose --profile mediamtx up -d     # add the MediaMTX media router
docker compose --profile monitoring up -d   # add Prometheus exporter
```

### 3. Open & first-time setup

Open **`https://localhost`** (or your `DOMAIN`). On a fresh install the login screen offers a
**first-run admin** form — create the admin account, then sign in and complete the Setup
Wizard (language, system check, storage). Subsequent users are managed under **Users** (admin).

### Default paths & volumes

Data lives in the `castcore_data` Docker volume, mounted at `/data` inside the containers:

| Path | Purpose |
| --- | --- |
| `/data/media` | media library sources |
| `/data/recordings` | recordings/replay output |
| `/data/logs`, `/data/backups`, `/data/mounts`, `/data/thumbnails` | logs, backups, mounts, assets |

Postgres, Redis and Caddy use their own named volumes. **Storage:** local folders work out of
the box; SMB/CIFS is supported (prefer host-side mounts; in-container mounting needs extra
capabilities). NFS/SFTP/WebDAV/rclone/cloud are **not implemented yet**.

### Updates

```bash
git pull
docker compose up -d --build      # rebuilds images; migrations run automatically on start
```

### Backup & restore

Use **Backup / Restore** in the UI (DB + config as gz-JSON; secrets stay encrypted). Keep the
`ENCRYPTION_KEY` with your backups (stored separately). See
[Deployment](docs/DEPLOYMENT.md) for details.

### Troubleshooting (install)

- **Can't reach `https://localhost`** — check `docker compose ps`; the `caddy` and `backend`
  services must be healthy. With a self-signed localhost cert, accept the browser warning.
- **Backend keeps restarting** — usually a missing/invalid `SECRET_KEY`/`ENCRYPTION_KEY` or
  `POSTGRES_PASSWORD`; check `docker compose logs backend`.
- **Can't log in on a fresh install** — the first-run admin form appears only while no user
  exists; if you created one already, sign in with it.
- **FFmpeg "vulnerable" warning** — should not appear with the default `copy` build (≥ 8.1.2);
  it is expected only if you switched to `FFMPEG_VARIANT=apt` (7.1.x < 8.1.2). See
  [FFmpeg requirements](docs/en/admin-guide/ffmpeg-requirements.md).

### Native install (experimental)

> ⚠️ The native scripts exist but are **not fully verified** — Docker is recommended.

```bash
sudo ./scripts/install.sh      # Debian 12 / Ubuntu LTS
sudo ./scripts/update.sh
sudo ./scripts/uninstall.sh
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — strategy, stack, target architecture
- [Data model](docs/DATA_MODEL.md) — entities & relationships
- [API](docs/API.md) — REST + WebSocket surface
- [Deployment](docs/DEPLOYMENT.md) — Docker-first & native install, backup/restore, upgrade
- [Local dev & testing](docs/LOCAL_DEV.md) — run the full stack on Windows via Docker Desktop
- [Security](docs/SECURITY.md) — auth, roles, secret handling, hardening
- [Roadmap](docs/ROADMAP.md) — milestone plan (Phase 1–4)

## Internationalisation

CastCore is fully bilingual (Deutsch / English) from day one. Language is chosen in the
Setup Wizard and per user; no UI strings are hard-coded. Translations live in
`frontend/src/i18n/{de,en}.json`; the backend returns translatable error **codes**.

## Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) runs on every push and pull request:

- **Backend** — `ruff` (lint), `mypy` (type check), `pytest` (unit + API integration tests
  against a Postgres service).
- **Frontend** — `npm ci`, ESLint, and the `tsc` + Vite build.
- **Docs** — `scripts/check_docs.py` (structure, DE/EN parity, manifest, internal links).
- **Compose** — `docker compose config` validation.

A separate **manual** workflow (`.github/workflows/e2e.yml`, `workflow_dispatch`) runs a
full-stack end-to-end stream-lifecycle test; it is not part of the per-PR gate because it
boots the whole stack. Run the same checks locally; the commands are listed in
[`CONTRIBUTING.md`](CONTRIBUTING.md#continuous-integration).

## License

See [LICENSE](LICENSE). Branding assets in `branding/` follow the CastCore brand guide.

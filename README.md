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
Redis), auto-restart; monitoring + Prometheus exporter; **FFmpeg version detection &
safe-media mode** (CVE-2026-8461 mitigation); local + SMB/CIFS storage; media library,
playlists, channels (HLS/EPG), recording, scheduler, notifications, backup/restore; MediaMTX
ingest (status + as a source); platform OAuth (YouTube/Twitch) with **metadata push** and a
**readiness check**; a full
bilingual docs/help system; and CI for backend (ruff/mypy/pytest incl. API integration
tests), frontend (eslint/build), docs and compose, plus a manual full-stack E2E workflow.

**Known gaps / not yet:**
- A patched **FFmpeg ≥ 8.1.2** is not yet the verified default binary (images ship Debian's
  build; a static-build path + runtime warnings are in place — see
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

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env — at minimum set the secret keys and the admin bootstrap values
docker compose up -d
# open https://localhost (or your configured DOMAIN) and complete the Setup Wizard
```

Optional service profiles:

```bash
docker compose --profile mediamtx up -d     # add the MediaMTX media router
docker compose --profile monitoring up -d   # add Prometheus exporters
```

## Native install (no Docker)

> ⚠️ The native install path exists but is **not yet fully verified** — Docker is the
> recommended and tested deployment.

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

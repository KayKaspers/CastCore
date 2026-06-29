# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What CastCore is

CastCore is a self-hosted **streaming operations suite** — a control plane for FFmpeg
streams, media sources, network/cloud storage, platform metadata, multi-output streaming,
monitoring, recording and linear channels. It is **not** an "FFmpeg web wrapper": it
manages sources, analyses media, plans streams, supervises FFmpeg safely, monitors outputs,
explains failures in plain language and offers fallbacks. Linux is the runtime target;
development happens on Windows via Docker Desktop. Bilingual **DE/EN** is a hard requirement.

The authoritative concept is [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md); the chronological
record of what actually landed is [`CHANGELOG.md`](CHANGELOG.md).

## Workflow & roles (project-specific — follow these)

- **Nova plans. Claude implements. Cursor reviews.** Implement only the next step Nova
  defined. **No large architectural changes, no new frameworks (without justification), no
  sweeping rewrites** without Nova.
- GitHub is the single source of code truth. Nextcloud is only storage for prompts, reviews,
  branding and exports.
- Standards: Docker-first · Documentation-first · Security-first · DE/EN · beginner-friendly ·
  modular · no hardcoded secrets · keep `.env.example` and the README current.
- Support link may appear **discreetly** (README, footer, About, docs) — no pop-ups, no
  paywall, no aggressive donation prompts, no features gated behind donations.

**Mandatory report after every step** (Rückmeldung an Nova): (1) what was implemented,
(2) which files changed, (3) problems hit, (4) open points, (5) risks, (6) tests run,
(7) whether README/docs were updated, (8) recommended next step.

## The documentation golden rule

> **No feature change without a documentation update.** (See [`CONTRIBUTING.md`](CONTRIBUTING.md).)

If a change touches code, UI, API, data model, deployment, config, security, CLI, install or
behaviour, update the matching **German *and* English** pages in the same change
(`docs/de/...` and `docs/en/...`), keep `docs/docs-manifest.json` current, and make
`python scripts/check_docs.py` pass (it regenerates `docs-status.json` + `nav.json` — commit
the result). UI strings are never hardcoded: they live in `frontend/src/i18n/{de,en}.json`;
the backend returns translatable error **codes** (e.g. `error.preflight.source_unreachable`),
not English strings. Update `CHANGELOG.md` when relevant.

## Commands

The whole stack is Docker-first; you don't need local Python/Node. The `Makefile` wraps the
common ones (`make up`, `make down`, `make logs`, `make ps`, `make migrate`, `make test`).

```bash
# Run the full stack (auto-runs alembic migrations on backend start)
cp .env.example .env          # set SECRET_KEY, ENCRYPTION_KEY, POSTGRES_PASSWORD, DOMAIN
docker compose up -d --build
docker compose ps             # wait for healthy; app at https://localhost (self-signed)

docker compose logs -f backend process-manager
docker compose down           # stop, keep data volumes
docker compose down -v        # stop + WIPE all data
docker compose --profile mediamtx up -d      # + MediaMTX router
docker compose --profile monitoring up -d    # + Prometheus exporter
docker compose exec backend alembic upgrade head   # manual migration
```

### CI checks — reproduce the four CI jobs locally before pushing

CI (`.github/workflows/ci.yml`) gates every PR. Run the same checks in throwaway containers
(works with no host toolchain):

```bash
# Backend: lint + type-check + tests (unit + API integration; integration needs Postgres)
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && ruff check app && mypy && pytest -q"

# Frontend: lint + tsc + Vite build
docker run --rm -v "$PWD/frontend":/app -w /app node:20-alpine sh -c "npm ci && npm run lint && npm run build"

# Docs structure / DE-EN parity / manifest / links
python scripts/check_docs.py

# Compose validation (any values work)
SECRET_KEY=x ENCRYPTION_KEY=x POSTGRES_PASSWORD=x docker compose config --quiet
```

With a local toolchain instead:

```bash
cd backend  && python -m pip install -e ".[dev]" && ruff check app && mypy && pytest
cd frontend && npm ci && npm run lint && npm run build        # npm run dev → :5173 (proxies /api)
```

- **Run one backend test:** `pytest tests/test_foo.py::test_bar -q` (from `backend/`, or via
  the `backend` container). `asyncio_mode = "auto"` — async tests need no decorator. Integration
  tests use a dedicated `castcore_test` database derived from the `POSTGRES_*` env vars; external
  services (OAuth, etc.) are mocked.
- **E2E** is separate and **manual** (`.github/workflows/e2e.yml`, `workflow_dispatch`); it boots
  the whole stack and runs `backend/e2e_stream.py` through the create→start→logs→stop lifecycle.

## Architecture

Seven Compose services on one bridge network (see [`docker-compose.yml`](docker-compose.yml)):
`caddy` (TLS/routing) → `frontend` (built SPA, nginx) + `backend` (FastAPI) → `postgres` +
`redis`, plus `process-manager` and `worker`; optional `mediamtx` and `prometheus` via profiles.

**The central design decision: Process Manager ≠ Worker.**

- **`process_manager/`** — a standalone asyncio **supervisor** for long-running FFmpeg
  processes (one per active output): start/stop/restart, reconnect, fallback, health scoring
  from parsed FFmpeg progress + psutil. This is *not* a task queue.
- **`worker/`** — **arq** (Redis-native async queue) for bounded jobs: media scan, ffprobe,
  thumbnails, backups, scheduled jobs.

**Redis is the live bus and control channel.** The Process Manager parses FFmpeg
stdout/stderr and publishes to Redis pub/sub; the backend subscribes and fans out to clients
over WebSocket (`/api/v1/.../ws`). Control commands (stop/restart) flow backend → Redis →
Process Manager. The backend's own lifespan runs two background loops: `run_status_consumer`
(reconciliation/notifications) and `run_scheduler` (cron-like jobs/channels) — see
[`backend/app/main.py`](backend/app/main.py).

**Postgres is the source of truth for *desired* state**; the Process Manager reconciles
*actual* process state toward it (a small control loop), so it survives restarts.

**Safe FFmpeg is non-negotiable (security-critical).** The FFmpeg Command Builder
(`backend/app/services/ffmpeg/`) produces ordered **argument lists** (global → input opts →
input → filters → output opts → output), validates every parameter, supports multi-in/out and
HLS/RTMP/SRT, and renders a **secret-masked preview**. It **never** builds a shell string. It
is heavily unit-tested — preserve that when touching it.

### Backend layout (`backend/app/`)

Python 3.12 · FastAPI · SQLAlchemy 2 async · Pydantic v2 · Alembic · asyncpg.

- `api/v1/endpoints/<feature>.py` — one router file per feature; assembled in
  `api/v1/router.py`. Shared deps (auth, RBAC, DB session) in `api/deps.py`.
- `services/<module>.py` (and packages `services/ffmpeg/`, `services/platform/`) — business
  logic. Endpoints stay thin; logic lives in services.
- `models/` SQLAlchemy ORM · `schemas/` Pydantic I/O · `core/` config/security · `db/` session
  · `i18n/` · `migrations/` Alembic.
- API is versioned under `/api/v1`; Swagger at `/api/docs`, OpenAPI at `/api/openapi.json`.
  CORS is only relaxed (for the Vite dev server) when **not** in production.

### Frontend layout (`frontend/src/`)

React 18 · TypeScript · Vite · Tailwind (CastCore brand tokens, dark-first) · i18next ·
TanStack Query · Zustand · react-router. `pages/` route screens · `components/` shared UI ·
`lib/` (incl. the typed API client / data hook) · `i18n/{de,en}.json` · `styles/`.

### Conventions that matter

- **Secrets** (stream keys, OAuth/SMB credentials) are encrypted at rest with **Fernet**
  (`ENCRYPTION_KEY` from the env, kept *out* of the repo and backed up separately), masked in
  UI and previews, and never logged.
- **Network calls** to sources/platforms must time out, retry and report status — the network
  is assumed untrusted/unstable.
- **Storage** today: local + SMB/CIFS only. NFS/SFTP/WebDAV/rclone/cloud are designed but **not
  implemented** — don't assume they exist.
- **Hardening:** `worker` runs `cap_drop: ALL` + non-root (it analyses untrusted media);
  `backend`/`process-manager` still run as root with `no-new-privileges` only.
- Persistent data lives in the `castcore_data` volume mounted at `/data` (`media`, `recordings`,
  `logs`, `backups`, `mounts`, `thumbnails`).

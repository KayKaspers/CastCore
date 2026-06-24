# Changelog

All notable changes to CastCore are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses semantic versioning.

## [Unreleased]

### Added — Phase 1: storage sources (local + SMB)
- Models `storage_sources` + `smb_sources` (migration `0003`); SMB passwords encrypted
  at rest (Fernet), write-only over the API (`has_password` flag only).
- `storage_service`: reachability test (local readable / SMB TCP 445), `mount.cifs`
  mount via a 0600 credentials file (shell-free, password never on the command line),
  unmount, and a path-traversal-confined media-aware directory browser.
- Endpoints `/storage-sources` (local + SMB create, test, mount, unmount, browse).
- Frontend Sources page: create local/SMB, test/mount/unmount, browse with media badges
  and "copy path" to paste into a stream job.
- Verified: local browse + traversal blocked (400); SMB test/mount fail gracefully in the
  unprivileged container (documents host-mount preference); password never leaked.

### Added — Phase 1: preflight check
- `preflight_service`: runs ffprobe against a job's input and checks input/streams
  (has video / has audio), enabled outputs, destination URL & stream key, and recording
  disk space; aggregates to 🟢/🟡/🔴.
- Endpoint `POST /stream-jobs/{id}/preflight`; UI shows a per-check report with badges
  before starting (DE/EN `preflight.*` labels).

### Fixed
- `get_current_user` now returns 401 (not 500) for a token whose `sub` is not a UUID.

### Added — Phase 1: live logs (WebSocket) + Stream Health Assistant
- Process Manager pumps FFmpeg stderr/stdout line-by-line to per-job Redis channels
  (`castcore:logs:<job_id>`), parses progress (fps/bitrate/speed/frame) to
  `castcore:status`, and tags lines with a translatable failure **hint** code.
- Backend WebSocket endpoints `/ws/logs/{job_id}` and `/ws/status` (token via query
  param) relay Redis → client, with disconnect detection.
- Frontend: live log panel per stream job (auto-scroll, error highlighting, live badge)
  and a plain-language health hint banner (DE/EN `loghint.*`).
- Verified end-to-end across containers: live FFmpeg output streamed to a WS client,
  and a failing input correctly surfaced the `source_missing` hint.

### Added — Phase 1: frontend (Login, Setup, Dashboard, Streams)
- API client with automatic JWT refresh and i18n error-code mapping; zustand auth store
  (token persistence, role checks); protected routing (react-router).
- Pages: **Login** (incl. first-run admin creation), **Setup Wizard** (step states,
  system check), **Dashboard** (system health + live job count), **Stream Jobs**
  (list, create form, start/stop/restart, masked command preview, delete), **Resources**
  (FFmpeg-profile & destination management with encrypted stream keys).
- Branded dark UI shell (sidebar nav, DE/EN switch, logout) on the CastCore tokens;
  reusable UI primitives. Verified: frontend image builds (tsc clean) and serves via Caddy.

### Added — Phase 1: streaming core & Process Manager wiring
- Streaming ORM models: `ffmpeg_profiles`, `destinations`, `stream_jobs`, `inputs`,
  `outputs`, `process_status`; migration `0002_streaming`.
- `stream_service`: assembles per-output FFmpeg argv from stored job/profile/destination
  via the Command Builder (one supervised process per enabled output), resolving &
  appending decrypted RTMP stream keys.
- Redis control channel: backend publishes start/stop/restart; the **Process Manager**
  now subscribes to `castcore:control`, spawns/stops FFmpeg via `subprocess_exec`
  (shell=False) and publishes state to `castcore:status`.
- Endpoints: FFmpeg-profile CRUD, destination CRUD (encrypted write-only stream keys),
  stream-job CRUD with nested inputs/outputs, `/preview`, `/start`, `/stop`, `/restart`
  (responses return masked command previews).
- Tests for argv assembly + stream-key masking (no DB needed).

### Added — Phase 1: data foundation, auth & setup
- SQLAlchemy 2.0 async ORM models: `users`, `roles`, `user_roles`, `sessions`,
  `api_tokens`, `settings`, `setup_state`, `audit_events`; `Base.metadata` wired into
  Alembic; first migration `0001_initial` (creates schema + seeds admin/operator/viewer).
- Async DB engine, session factory and `get_db` dependency.
- Auth service: argon2 login, JWT access + persisted hashed refresh tokens with
  **rotation** and revocation; `get_current_user` + `require_roles` RBAC dependencies.
- Endpoints: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`;
  `/setup/state|admin|syscheck|step/{step}|complete`; admin-only `/users` CRUD.
- Setup wizard logic: ordered step state, first-run admin bootstrap (only while no user
  exists), system check (FFmpeg/ffprobe presence, data dirs writable, free disk).
- Tests for security primitives (hashing, Fernet, JWT, masking).

### Added — initial scaffold (Phase 1 start)
- Project architecture & concept docs: `docs/ARCHITECTURE.md`, `DATA_MODEL.md`,
  `API.md`, `DEPLOYMENT.md`, `SECURITY.md`, `ROADMAP.md`.
- Tech-stack decision: **Python/FastAPI** backend, React/TS frontend, PostgreSQL,
  Redis, dedicated FFmpeg Process Manager, arq worker.
- Docker-first deployment: `docker-compose.yml` (frontend, backend, process-manager,
  worker, postgres, redis, caddy; optional mediamtx/monitoring profiles), `.env.example`.
- Native install tooling: `scripts/install.sh`, `update.sh`, `uninstall.sh`, systemd units.
- Backend skeleton: FastAPI app, config, security primitives (argon2, Fernet, JWT,
  secret masking), translatable error codes, health endpoints, Alembic setup.
- **FFmpeg Command Builder** (security-critical) with safe argv construction, parameter
  validation, secret masking and a unit-test suite.
- Frontend skeleton: React + Vite + Tailwind wired to the CastCore brand tokens,
  i18next with full **DE/EN** translations and error-code strings, branded landing shell.
- Worker and Process Manager service skeletons (Dockerfiles + entrypoints).
- Corporate design package integrated under `branding/`; favicons & logos wired into
  the frontend.

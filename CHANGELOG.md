# Changelog

All notable changes to CastCore are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses semantic versioning.

## [Unreleased]

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

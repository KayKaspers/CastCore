# Changelog

All notable changes to CastCore are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses semantic versioning.

## [Unreleased]

### Added — user management page (all 21 mandatory UI pages now present)
- Admin **Users** page (`/users`): create users, toggle roles (admin/operator/viewer),
  enable/disable accounts, reset passwords, delete — with self-protection (can't disable
  or delete your own account). Backed by the existing `/users` API.
- Docs: `user-guide/users-roles.md` filled (DE+EN); manifest updated.
- This completes the 21 mandatory UI pages from the product brief.
- Verified: create, role change, deactivate, password reset and delete all work.

### Added — update / version info
- `update_service` reports the running version, environment, deployment mode
  (docker/native, auto-detected) and the DB **migration status** (current vs. head
  Alembic revision, up-to-date flag). CastCore does not self-update; this is informational.
- Endpoint `GET /update/state` (admin) and an **Updates** page showing version + migration
  status with a link to the update guide.
- Docs: `user-guide/updates.md` filled (DE+EN, Docker & native update, rollback via backup);
  manifest `updates` feature added.
- Verified: reports docker deployment with DB at head and up_to_date=true.

### Added — stream self-healing (auto-restart on failure)
- The status consumer now auto-restarts a failed output per the job's `fallback_policy`
  (`auto_restart`, `max_retry`, `retry_delay_s`): on an unexpected failure it rebuilds the
  output argv and re-issues a start after a delay, up to max retries; a successful run
  resets the counter, a deliberate stop never restarts. The attempt count is written to
  `process_status.reconnect_count` (visible in Monitoring).
- Stream-job create form gains an **auto-restart** toggle + max retries; `fallback_policy`
  exposed on the job. Docs: self-healing section in `streams.md` (DE+EN).
- Verified: a simulated crash triggered an auto-restart and bumped the reconnect count.

### Added — audit log
- `audit_service` records security-relevant actions to the existing `audit_events` table:
  **login**, **stream start/stop/restart**, **backup create/restore**, **user create/delete**
  (actor, action, target, IP, timestamp). Best-effort — auditing never breaks the action.
- The audit log is now **excluded from backup/restore** so the trail survives a restore.
- Endpoint `GET /audit` (admin, filter + pagination) and an admin **Audit log** page.
- Docs: audit section added to `admin-guide/security.md` (DE+EN); manifest updated.
- Verified: user create/delete and stream start/stop appear in the audit trail.

### Added — internal HLS web player (channel preview)
- `HlsPlayer` component (hls.js, native HLS on Safari) and a **Preview** button on the
  Channels page that plays a running channel's HLS right in the dashboard.
- Docs: in-browser preview section added to `channels.md` (DE+EN).
- Verified: frontend builds with hls.js (tsc clean); a running channel serves the HLS
  playlist with content-type `application/vnd.apple.mpegurl`.

### Added — dry-run / test stream (completes Phase 2)
- `dry_run_service` runs a short (~5s) test encode of the job's source through its profile
  into a throwaway file (no live output, no network), then reports success, encoding
  **speed**, **fps**, a plain-language message and the last log lines.
- Endpoint `POST /stream-jobs/{id}/dry-run`; UI **Dry-run** button + report panel
  (speed < 1× highlighted). Docs: dry-run section added to `preflight-checks.md` (DE+EN);
  manifest stream-jobs api routes updated.
- Verified: a good lavfi job reports ok with ~22× speed; a missing-file job reports the
  FFmpeg error.

### Added — full FFmpeg profile editor (incl. GPU encoders)
- Dedicated **FFmpeg profiles** page (`/profiles`) with the complete option set: codec
  (incl. GPU **NVENC/QSV/VAAPI**), bitrate, resolution, FPS, preset, tune, GOP,
  pixel format, audio codec/bitrate/disable, `filter_complex` and free-form expert args.
- Create **and edit** existing profiles; **live command preview** via `/ffmpeg/preview`
  (masked stream key). Profiles moved out of the Resources page into their own nav entry.
- Docs: `reference/ffmpeg-profiles.md` filled (DE+EN) including GPU notes.
- Verified: a GPU profile round-trips (create/edit), the preview renders all fields, and
  an invalid codec is rejected (400) by the command-builder whitelist.

### Added — settings service (persisted language + instance settings)
- `settings_service` for instance-wide settings (`instance_name`, `default_language`)
  stored in the `settings` table; per-user profile updates on the `User` model.
- Endpoints `/settings/me` (GET/PATCH own profile incl. **persisted language**) and
  `/settings` (admin GET/PATCH instance settings).
- Frontend **Settings** page (`/settings`): profile with language switch saved to the
  backend (follows the user across devices/logins), admin instance settings, link to the
  setup wizard. Main-nav "Settings" now points here.
- Docs: `user-guide/settings.md` extended with profile/instance sections (DE+EN);
  manifest `settings` feature added.
- Verified: per-user language change persists in the DB; instance settings round-trip.

### Added — notification triggers wired (backup / preflight / source)
- The `backup_done`, `preflight_failed` and `source_offline` events now actually fire:
  `backup_done` after every backup (manual or scheduled), `preflight_failed` when a
  preflight is red, `source_offline` when a source test fails. `preflight_failed` is now
  in the subscribable event list with a friendly title.
- Docs: `user-guide/settings.md` filled (DE+EN) documenting notification channels, all
  events and the scheduler.
- Verified: a webhook subscribed to all three received "backup created", "source offline"
  and "preflight failed" notifications end-to-end.

### Added — thumbnail / asset management (secure uploads)
- `assets` model (migration `0013`) + `platform_metadata.thumbnail_asset_id`.
- `asset_service` with **secure image upload**: magic-byte type validation (PNG/JPEG/
  WebP/GIF, not extension-based), 10 MB size limit, generated safe filenames (never the
  user's name on disk), best-effort PNG/JPEG dimension parsing, content de-dup by sha256.
- Endpoints `/assets` (operator): upload, list, serve, delete. Platform metadata accepts
  `thumbnail_asset_id`; resolved metadata returns `thumbnail_url` and a `thumbnail.missing`
  warning.
- Frontend: Assets page (upload + grid via auth-aware `AuthImg`), thumbnail picker in the
  metadata editor, DE/EN strings + upload error messages.
- Docs: `user-guide/metadata-thumbnails.md` filled (DE+EN); manifest `assets` feature added.
- Verified: valid PNG accepted (mime + dimensions), non-image rejected (400
  `unsupported_type`), file served, thumbnail resolved into metadata.

### Added — bilingual documentation & in-app help system
- Full bilingual docs tree under `docs/de` (primary) + `docs/en` (parallel), structurally
  synchronized: getting-started, user-guide, admin-guide, developer-guide, api, reference,
  troubleshooting (74 pages per language). Cornerstone pages written in full; the rest are
  non-empty, templated stubs with descriptions + TODOs.
- **Documentation system**: `docs/docs-manifest.json` (feature → docs/UI/API/model map),
  `scripts/check_docs.py` (validates DE/EN parity, manifest references, empty pages,
  stale `lastReviewed`; regenerates `docs/docs-status.json` and `docs/nav.json`),
  `docs/templates/` (page/troubleshooting/feature templates, DE+EN), and a
  `.github/workflows/docs-check.yml` CI check (parity + broken internal links).
- **In-app help**: `/docs` viewer (renders the Markdown via `marked`, sidebar nav from
  `nav.json`, search, breadcrumbs, language-aware, "back to app"); a **Help** entry in the
  main navigation; a reusable `HelpLink` component and `helpLinks` map wiring UI areas
  (stream jobs, sources/SMB) and the FFmpeg log-hint banner to the matching docs pages.
  Docs are bind-mounted read-only into the frontend container (single source of truth).
- **Process rule** documented in `CLAUDE.md`, `CONTRIBUTING.md` and the documentation-rules
  page: *no feature change without a documentation update* (DE + EN).
- Verified: `check_docs.py` reports 0 errors / 0 warnings across 74 pages per language and
  generated `docs-status.json` + `nav.json`.

### Added — platform metadata + description templates
- `platform_metadata` (migration `0012`): per stream-job, per-platform title, description
  template, category, tags, language, visibility, scheduled start (unique per job+platform).
- `metadata_service` resolves description/title templates with placeholders
  `{stream_title} {date} {time} {platform} {category} {tags} {source_name} {server_name}
  {channel_name}`; returns resolved metadata + warnings for pre-start review.
- Endpoints: list/upsert/delete `/stream-jobs/{id}/metadata/{platform}`, `…/resolved`,
  and generic `/metadata/resolve` + `/metadata/placeholders`.
- Frontend metadata editor (per-platform tabs, template field with placeholder hint,
  "resolve preview") reachable from each stream job.
- Verified: template resolved title/description with all placeholders filled correctly.

### Added — Phase 3: channel health + fallback
- The status consumer now reconciles **channel** status from the real Process Manager
  state (running/stopped/failed), so channel crashes become visible (no longer optimistic).
- Channel start drops media that no longer exists on disk (one missing file can't kill the
  channel) and falls back to a configured loop video (`channels.fallback_uri`, migration
  `0011`) when no playlist media is playable; a clean error if neither is available.
- Channels UI auto-refreshes status (3s) and exposes a fallback-video field.
- Verified: channel status reconciled on start/stop; empty playlist + fallback starts;
  no media + no fallback returns 400.

### Added — Phase 3: linear channels (start)
- `channels` model (migration `0010`) + `channel_service`: 24/7 playout that loops a
  playlist via the FFmpeg concat demuxer into a rolling HLS output (supervised by the
  Process Manager through the control channel).
- EPG/XMLTV generation (now+next from playlist item durations) and an M3U lineup export.
- Endpoints: channel CRUD + start/stop (operator); **public** HLS serving
  (`/channels/{id}/hls/{path}`), `/channels/{id}/epg.xml`, `/channels/export.m3u` for
  IPTV players. Frontend Channels page (create from playlist, start/stop, HLS/EPG links,
  M3U lineup).
- Verified live: a channel started, produced a served HLS playlist with .ts segments,
  generated XMLTV programmes and appeared in the M3U export.

### Added — Phase 2: playlists (completes Phase 2)
- `playlists` + `playlist_items` (migration `0009`) with modes sequential/shuffle/loop.
- `playlist_service.resolve` turns a playlist into an ordered list of absolute media
  paths with per-item and total duration (the basis for Phase 3 channel playout).
- Endpoints `/playlists` (CRUD, add/remove items, reorder, resolve); Playlists UI page
  with media picker, up/down reordering, mode switch and total-duration readout.
- Verified: items added, reordered, and resolved to abs paths + correct total duration.

### Added — Phase 2: scheduler
- `scheduler_entries` (migration `0008`) + `scheduler_service` with a background loop
  (FastAPI lifespan, alongside the status consumer) evaluating due entries every 20s.
- Schedule types: once / interval / daily (HH:MM UTC). Actions: stream_start,
  stream_stop, backup, scan. Each run records `last_run_at`/`last_status` and advances
  `next_run_at`.
- Endpoints `/scheduler` (CRUD, `/run` for run-now); Scheduler UI page with action +
  target pickers and schedule fields.
- Verified: daily next-run computed correctly, run-now executed a backup, and a due
  interval entry fired via tick() and rescheduled itself.

### Added — Phase 2: recording & replay
- `recordings` table + `stream_jobs.recording_enabled`/`recording_retention_days`
  (migration `0007`).
- When a recording-enabled job starts, the stream service spawns a synthetic mp4
  recording output (timestamped filename in the recordings dir) alongside the live
  outputs and tracks it; the status consumer finalizes the recording (size, duration,
  state) when the process exits.
- Endpoints `/recordings` (list, filter by job), download, delete; stream-job create
  exposes `recording_enabled`, plus a `/stream-jobs/{id}/recording` toggle.
- Frontend Recordings/Replay page (state, duration, size, download) and a recording
  checkbox in the job create form.
- Verified: a recording-enabled job produced a file that finalized to completed with
  correct duration/size on stop.

### Added — Phase 2: monitoring
- Process Manager samples per-FFmpeg-process CPU% and RSS via psutil (every 3s) and
  publishes them (plus pid) on the status channel; the consumer persists them to
  `process_status` alongside the parsed fps/bitrate/speed.
- Endpoints `/monitoring/system` (CPU/RAM/disk/ffmpeg count via psutil) and
  `/monitoring/outputs` (live per-output metrics joined with job/destination), readable
  by any authenticated user.
- Auto-refreshing Monitoring dashboard (system gauges + per-output table; speed < 1×
  highlighted).
- Verified live: a real-time (`-re`) stream reported running fps≈29, speed≈0.95×,
  CPU≈8%, RSS≈400 MB through the full PM→Redis→DB→API path.

### Added — Phase 2: notifications + status reconciliation
- Background **status consumer** in the backend (FastAPI lifespan) subscribes to
  `castcore:status`, reconciles per-output `process_status` and `StreamJob.status` from
  the Process Manager's actual state (closes the PM→DB→UI loop), and fires events on
  transitions.
- `notifications` model (migration `0006`) + `notification_service` with webhook /
  Discord / Slack / Gotify / Telegram / email channels; connection params encrypted
  (write-only). Events: stream_started/stopped/failed, source_offline, backup_done, test.
- Admin endpoints (CRUD, `/events`, `/test`) and a Notifications UI page with
  channel-specific fields and event selection.
- Verified end-to-end: a real status transition reconciled job status in the DB and
  delivered stream_started/stopped to a webhook; secret URL never leaked.

### Added — Phase 2: media library (start)
- Models `media_library_items` + `media_probe_data` (migration `0005`).
- `media_service.scan_source`: walks a storage source, indexes files (kind by
  extension, size, mtime), runs ffprobe on media and stores container/duration/codecs/
  resolution/fps/bitrate, marks `streamable` and `problem_flags`; incremental (skips
  unchanged files). Reusable by the worker later.
- Endpoints `/media/scan/{source_id}`, `/media` (filter by source/kind/streamable/search),
  `/media/{id}`, delete. Frontend Media Library page: pick source, scan, filter, table
  with codec/resolution/duration + "copy path" into a stream job.
- Verified: scanning the recordings folder indexed + probed 2 files as streamable h264
  with correct metadata; source delete cascades media away.

### Added — Phase 1: backup & restore (completes Phase 1)
- `backups` table (migration `0004`) and `backup_service`: self-contained logical dump
  of all application tables to gzipped JSON (no pg_dump version coupling); secrets stay
  encrypted in the artifact. Restore wipes & repopulates in FK order within a
  transaction; the `backups` table is excluded so history survives.
- Admin endpoints: create, list, download, restore (requires `?confirm=true`), delete.
- Frontend Backup/Restore page (create, download, confirm-guarded restore, delete).
- Verified round-trip: backup → delete data → restore brings it back; unconfirmed
  restore is rejected (400); users preserved.

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

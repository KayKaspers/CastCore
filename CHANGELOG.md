# Changelog

All notable changes to CastCore are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses semantic versioning.

## [Unreleased]

### Added — End-to-end stream lifecycle test (Phase 0, Step 4)
- `backend/e2e_stream.py`: a full-stack E2E driving the real lifecycle via the live API +
  Redis (backend + Process Manager + status consumer): create job → command preview → start →
  process status `running` → receive logs (Redis log channel) → output file grows → stop →
  final status `stopped`, with full cleanup afterwards.
- Uses only **safe local** media (lavfi `testsrc`, H.264, audio disabled, MPEG-TS to a file) —
  no external services, no risky codecs. A vulnerable FFmpeg (< 8.1.2) does **not** fail the
  test (only the non-blocking version warning is affected).
- CI: new manual `.github/workflows/e2e.yml` (`workflow_dispatch`) that builds/boots the core
  stack and runs the script; kept out of the per-PR `ci` gate because it boots the whole stack.
  The script ships in the backend image (`/app/e2e_stream.py`).
- Verified locally against the running stack: status reached `running`, 22 log lines received,
  output grew 12.8 MB → 25.7 MB, stopped cleanly.
- Docs: developer-guide `testing.md` (DE+EN) gains an E2E section; CONTRIBUTING notes it;
  check_docs green (77 pages).

### Security — FFmpeg PixelSmash / CVE-2026-8461 hardening
- **Audit**: all images (backend/process-manager/worker) ran FFmpeg/ffprobe **7.1.5 (< 8.1.2,
  vulnerable)**; real untrusted-decode paths are the media scan (ffprobe, incl. SMB), dry-run
  and preflight (all time-bounded); worker thumbnail/probe are still stubs; processes ran as
  root with no privilege restrictions and inherited secrets via env. Risk: **moderate**.
- **Version detection** (`app/core/ffmpeg_inspect.py`): parses FFmpeg/ffprobe versions, flags
  builds `< 8.1.2` as vulnerable (min configurable in code), and exposes a risky-codec
  blocklist (default `magicyuv`). Surfaced via:
  - `GET /api/v1/monitoring/ffmpeg` (authed) + a **FFmpeg security** panel on the Monitoring
    page (version, vulnerable/unknown/ok badge, safe-media flags).
  - **Preflight**: warns on a vulnerable FFmpeg and, for risky input codecs, blocks (red) when
    `BLOCK_RISKY_CODECS` + safe mode are on (else warns).
  - **Setup wizard** syscheck: an `ffmpeg_version` item (warns if vulnerable).
- **Safe media processing** (config/env): `SAFE_MEDIA_PROCESSING_ENABLED`,
  `MEDIA_AUTOTHUMBNAILS_ENABLED`, `BLOCK_RISKY_CODECS`, `RISKY_CODECS_BLOCKLIST`. Media scan
  flags risky-codec files (`problem_flags.risky_codec`); the media library shows a **Risky
  codec** badge. DE/EN i18n for all new strings.
- **Process hardening**: spawned FFmpeg processes get a **minimal, secret-free environment**
  (no SECRET_KEY/ENCRYPTION_KEY/DB creds). Compose: `no-new-privileges` on backend/PM/worker;
  worker additionally `cap_drop: ALL` and runs **non-root** (uid 10001). Verified the worker
  starts hardened with ffmpeg available.
- **Patched FFmpeg path**: Dockerfiles accept `--build-arg FFMPEG_VARIANT=static
  --build-arg FFMPEG_STATIC_URL=<8.1.2+ tarball>` to install a patched static build to
  `/usr/bin` (apt remains the default). `scripts/install.sh` now checks the FFmpeg version and
  warns if `< 8.1.2`.
- **Tests**: `test_ffmpeg_inspect.py` (version parse/compare, risky-codec, get_info) +
  `test_preflight.py` (risky-codec block, clean codec, vulnerable-version warn). Full backend
  suite **64 passed**. Real detection confirmed: 7.1.5 → vulnerable.
- **Docs**: new `admin-guide/ffmpeg-requirements.md` (DE+EN); security guide + env-vars +
  `troubleshooting/ffmpeg-errors.md` updated (DE+EN); manifest gains an `ffmpeg-security`
  feature; check_docs green (77 pages).
- **Caveat**: advisory details (8.1.2, MagicYUV) are operator-provided; the *active* mitigation
  is detection/warnings/safe-media — operators must supply a patched FFmpeg build. A real
  ≥8.1.2 binary was not installed in this environment (may not be published in this timeline).

### Added — API integration test suite (Phase 0, Step 3)
- New pytest integration suite exercising the FastAPI app in-process via httpx
  `ASGITransport` (no network; app lifespan / Redis loops not started). 22 new tests across
  `tests/test_api_{auth,rbac,streams,platform,system}.py`:
  - **auth**: setup status, admin bootstrap + conflict, login, refresh, logout, wrong
    password, bogus refresh, full 2FA flow (setup → verify → login gate), API-token lifecycle.
  - **rbac**: protected route needs a token, `/auth/me`, operator-gated `/stream-jobs`
    (viewer 403 / operator+admin 200), admin-only `/users`, inactive-user token rejected.
  - **streams**: stream-job CRUD, command preview (asserts stream-key masking), preflight.
  - **platform**: OAuth providers list (disabled without creds), authorize gating,
    platform-account status with a **mocked provider boundary** (encrypted tokens, no token
    leakage over the API), disconnect.
  - **system**: `/health`, `/system/health`, monitoring `/monitoring/system` (auth required).
- **DB strategy**: a dedicated `castcore_test` Postgres database, isolated from app/dev data.
  Schema via `Base.metadata.create_all`; each test truncates all tables and re-seeds the
  default roles; `get_db` is overridden to the test engine (`tests/conftest.py`). Connection
  from `POSTGRES_*`; DB name `TEST_DB_NAME` (default `castcore_test`); rate limiting disabled.
- **CI**: the `backend` job now runs a `postgres:16` service and the integration tests as part
  of `pytest`. Full suite **46 passed** locally (24 unit + 22 integration).
- **Fixed** a robustness bug surfaced by the new tests: `GET /monitoring/system` 500'd when
  `DATA_DIR` did not exist (e.g. before the volume is mounted) because
  `psutil.disk_usage(data_dir)` raised; it now falls back to `/`.
- Docs: developer-guide `testing.md` (DE+EN) gains an "API integration tests" section;
  CONTRIBUTING + README note the test DB; check_docs green (76 pages).

### Added — Full CI for backend, frontend and docs (Phase 0, Step 2)
- New consolidated GitHub Actions workflow `.github/workflows/ci.yml` with four jobs, all
  blocking on push/PR:
  - **backend**: `ruff check app`, `mypy`, `pytest` (installs `.[dev]`).
  - **frontend**: `npm ci`, `npm run lint` (ESLint), `npm run build` (`tsc` + Vite).
  - **docs**: `scripts/check_docs.py` + out-of-date guard + internal-link check.
  - **compose**: `docker compose config` validation.
- Replaced the docs-only `docs-check.yml` (its checks now live in `ci.yml`).
- **Backend tooling made green**: added `[tool.mypy]` config (`ignore_missing_imports`,
  `files=["app"]`) and `[tool.setuptools.packages.find] include=["app*"]` so
  `pip install -e ".[dev]"` works (setuptools otherwise trips over `app`/`tests`/`migrations`);
  fixed the two ruff findings it surfaced (unused `Path` import in `endpoints/channels.py`;
  f-string-without-placeholder in `ffmpeg/command_builder.py`). Verified in a clean
  `python:3.12-slim` container: editable install OK, ruff clean, mypy clean (95 files),
  pytest 24 passed.
- **Frontend tooling set up**: added ESLint 9 flat config (`eslint.config.js`) with
  typescript-eslint + react-hooks/react-refresh plugins and the matching devDependencies;
  committed `frontend/package-lock.json` so `npm ci` is reproducible; added a `typecheck`
  script. Verified in a Node 20 container: `npm ci` + lint (0 errors, 3 warnings) + build OK.
- Docs: README gains a **Continuous integration** section; `CONTRIBUTING.md` and
  `docs/LOCAL_DEV.md` document the exact local commands (incl. container-only paths);
  developer-guide `testing.md` (DE+EN) rewritten to describe the four CI jobs. check_docs
  green (76 pages).

### Added — Rate limiting for sensitive auth endpoints (Phase 0, Step 1)
- Redis-backed fixed-window rate limiter (`core/ratelimit.py`) on `POST /auth/login`,
  `/auth/refresh`, `/auth/2fa/verify`, `/tokens` (create) and `/setup/admin`. Over the limit
  → `429` with translatable code `auth.rate_limited` + `Retry-After` header. Default 10
  attempts / 300 s per client IP (first `X-Forwarded-For` hop); **fails open** if Redis is
  unreachable. Configurable via `RATE_LIMIT_ENABLED`, `RATE_LIMIT_AUTH_ATTEMPTS`,
  `RATE_LIMIT_AUTH_WINDOW_SECONDS` (env + compose + .env.example).
- `CastCoreError` gained an optional `headers` arg (for `Retry-After`).
- Frontend i18n: `error.auth.rate_limited` (DE/EN) — Login shows a clear message.
- Tests: `backend/tests/test_ratelimit.py` (6 tests: limit→429, bucket/identity separation,
  fail-open, disabled-by-setting, dependency enforcement, X-Forwarded-For identity).
  Whole backend suite green (24 passed). Verified live against the running stack:
  10×401 then 429 + `Retry-After`, fresh IP unaffected.
- Docs: security guide (DE+EN) corrected — replaced the inaccurate "rate limiting / CSRF /
  CSP" claim with the real state (rate limiting now implemented; HSTS/nosniff/Referrer-Policy
  present; **CSP not set**; API is Bearer-based so cookie-CSRF N/A). Env-vars reference +
  api/auth.md (429 note) + top-level `docs/SECURITY.md` updated. check_docs green (76 pages).
- Fixed a stale assertion in `tests/ffmpeg/test_command_builder.py` (argv tail is `-f flv
  <url>`); the builder was correct, the test expectation was wrong.

### Added — Platform OAuth account linking (YouTube/Twitch)
- New provider-agnostic OAuth integration to link real platform accounts. `PlatformAccount`
  model (migration `0015`) stores access/refresh tokens **Fernet-encrypted**, never returned
  by the API. Provider registry (YouTube/Google, Twitch) with env-configured client creds;
  a provider is enabled only when its client id + `PUBLIC_BASE_URL` are set.
- Flow: `POST /api/v1/oauth/{provider}/authorize` mints a signed, short-lived `state`
  (carries the initiating user, prevents CSRF) and returns the authorize URL;
  `GET /api/v1/oauth/{provider}/callback` (public browser redirect) verifies state, exchanges
  the code, links the account, and 303-redirects back to the UI. Account mgmt:
  `GET /platform-accounts`, `POST /platform-accounts/{id}/refresh`, `DELETE …/{id}`. Audited
  (connect/disconnect/token_refresh). External provider HTTP is isolated in
  `_post_token`/`fetch_account_name`.
- Config/compose/.env.example: `PUBLIC_BASE_URL`, `{YOUTUBE,TWITCH}_CLIENT_ID/SECRET`.
- Platforms page (`/resources`): "Connected platforms" — connect buttons (per enabled
  provider), linked-accounts list, disconnect, and OAuth-return notice; disabled providers
  show a config hint. DE/EN i18n.
- Docs: new `admin-guide/platform-oauth.md` (DE+EN) + env-vars reference + platforms
  cross-links; manifest gains a `platform-oauth` feature. check_docs green (76 pages).
- Verified in Docker with the provider HTTP boundary stubbed (9 assertions: provider gating,
  authorize URL, state roundtrip + mismatch rejection, providers/authorize endpoints,
  callback exchange + 303, tokens encrypted-at-rest + masked in API, refresh, bad-state error
  redirect, disconnect). Live end-to-end needs real YouTube/Twitch client credentials.

### Added — MediaMTX ingest as a stream source
- Active ingest paths can now feed a stream job: `GET /api/v1/mediamtx/sources` returns each
  **ready** path with a `pull_url` (internal RTSP), derived from the new `MEDIAMTX_RTSP_URL`
  base (env + compose + .env.example).
- Stream-job create form: a "Use from MediaMTX ingest…" selector appears next to Input URI
  when ≥1 path is live; picking one fills the URI with the pull URL and creates a `url` input
  with `reconnect` + `rtsp_transport=tcp`. DE/EN i18n.
- Docs: "use ingest as a source" sections in `mediamtx.md` (DE+EN) + env-variables reference;
  manifest updated. check_docs green (75 pages).
- Verified end-to-end in Docker by publishing a real RTMP test stream into MediaMTX
  (5 assertions: pull_url derivation, empty without publisher, listed with correct pull_url
  while publishing, source_type=rtmpConn, removed after publisher stops).

### Added — MediaMTX ingest status (read-only integration)
- New optional integration with the **MediaMTX** media router: `GET /api/v1/mediamtx/status`
  returns `{enabled, reachable, paths}` by querying the MediaMTX v3 API (`/v3/paths/list`),
  normalizing each path (ready/source/tracks/bytes/readers). Never mutates MediaMTX; failures
  degrade to `reachable:false` instead of erroring.
- Config: `MEDIAMTX_ENABLED` / `MEDIAMTX_API_URL` (env + compose `x-common-env`).
- `deploy/mediamtx/mediamtx.yml`: grant `api`/`metrics` to the internal-network user so the
  control plane can read status (API port stays internal-only, never published to the host).
- Monitoring page: an **Ingest (MediaMTX)** panel (reachability badge + live path table:
  status/source/tracks/received/readers), shown only when enabled. DE/EN i18n.
- Docs: new `admin-guide/mediamtx.md` (DE+EN) + ingest section in `monitoring.md`; manifest
  gains a `mediamtx` feature. check_docs green (75 pages). Verified end-to-end in Docker
  against a live MediaMTX container (3 assertions: disabled, enabled+reachable, enabled+
  unreachable-no-crash).

### Added — Active session management
- Users can see and manage their login sessions: `GET /api/v1/auth/sessions` (active,
  non-expired; the current one flagged), `DELETE /api/v1/auth/sessions/{id}` (sign out one),
  `POST /api/v1/auth/sessions/revoke-others` (keep current, drop the rest). Audited.
- Access tokens now carry a `sid` claim (the session id) so the UI/API can mark "this
  device"; a new `get_current_session_id` dependency reads it (None for API tokens).
- Settings → Active sessions UI: list (device/IP/since), "This device" badge, per-session
  sign-out, "sign out all others". DE/EN i18n.
- Docs: sessions sections in `api/auth.md` and `settings.md` (DE+EN); manifest updated;
  check_docs green. Verified end-to-end in Docker (6 assertions: 3 logins, exactly one
  current, revoke one 3→2, revoke-others leaves only current, revoked device sees no
  current, unknown id → 404).

### Added — Personal access tokens (API tokens)
- Programmatic API auth via long-lived **personal access tokens** (`cc_`-prefixed),
  stored hashed only. Bearer auth now accepts either a JWT or an API token — the prefix
  disambiguates; the token authenticates as its owner with the owner's roles.
- Endpoints (per-user): `GET /api/v1/tokens`, `POST /api/v1/tokens`
  (`{name, expires_in_days?}` → plaintext `token` returned **once**),
  `DELETE /api/v1/tokens/{id}`. Optional expiry honoured; `last_used_at` tracked; audited
  as `token.create` / `token.revoke`.
- Settings → API tokens UI: create (one-time reveal + copy), list (name/last-used/expiry),
  revoke. DE/EN i18n.
- Docs: full section in `api/auth.md` (incl. 2FA endpoints now listed) + `settings.md`
  (DE+EN); manifest updated; check_docs green. Verified end-to-end in Docker (7 assertions:
  create, prefix, list omits plaintext, token→/me, last_used, bogus→401, revoke, expiry).

### Added — Admin 2FA reset (recovery)
- `POST /api/v1/users/{id}/2fa/reset` (admin only) clears a user's 2FA when the second
  factor is lost; the secret is wiped and `totp_enabled` set false. Audited as
  `user.2fa_reset`.
- Users page (`/users`): a **2FA** column shows each user's status; **Reset 2FA** (with
  confirm) appears for users who have it enabled. DE/EN i18n.
- Docs: recovery now points at the real action in `security.md` and `users-roles.md`
  (DE+EN); manifest updated; check_docs green. Verified end-to-end in Docker (4 assertions:
  victim gated → reset → password-only login → 404 on unknown id; secret wiped in DB).

### Added — Phase 4: Two-factor authentication (2FA / TOTP)
- Per-user **TOTP** 2FA (RFC 6238), implemented with the standard library only
  (`backend/app/core/totp.py`) — compatible with Google Authenticator, Aegis, 1Password.
- New endpoints: `POST /auth/2fa/setup` (generate secret + `otpauth://` URI),
  `POST /auth/2fa/verify` (activate), `POST /auth/2fa/disable` (requires a valid code).
  `POST /auth/login` now accepts an optional `totp_code`; logins for 2FA-enabled users
  return `auth.totp_required` / `auth.totp_invalid` until a valid code is supplied.
- The TOTP secret is stored **encrypted at-rest** (Fernet) and never returned in clear text;
  `users.totp_enabled` added via migration `0014_totp`. `UserOut` now exposes `totp_enabled`.
- Frontend: Settings → Profile gains a **2FA** section (set up → scan/enter key → confirm →
  activate; disable with a code). Login shows a code field when 2FA is required. DE/EN i18n.
- Docs: 2FA sections in `admin-guide/security.md` and `user-guide/settings.md` (DE+EN);
  manifest updated. Verified end-to-end in Docker (setup/verify/login/disable, 8 assertions).

### Added — Phase 4: Prometheus metrics exporter
- `GET /api/v1/metrics` exposes system metrics (CPU/mem/disk/ffmpeg/jobs) and per-output
  stream metrics (fps/bitrate/speed/cpu/rss, labelled by `output_id`) in the standard
  Prometheus text format (no external client dependency; unauthenticated by convention,
  UUID-only labels).
- A preconfigured **Prometheus** service ships in the `monitoring` compose profile
  (`deploy/prometheus/prometheus.yml`, scrapes `/api/v1/metrics`).
- Docs: Prometheus/Grafana section added to `monitoring.md` (DE+EN); manifest updated.
- Verified: endpoint returns valid exposition format with `text/plain; version=0.0.4`.

### Docs — admin guide & troubleshooting filled (DE+EN)
- Wrote full content for `admin-guide/`: deployment, docker-compose, reverse-proxy, https,
  storage-mounts, secrets, logs — grounded in the actual compose/Caddyfile/install scripts.
- Wrote `troubleshooting/`: platform-errors, performance, docker, native-installation
  (symptom → causes → diagnosis → fix → logs).
- Placeholders 92 → 70; check_docs green (DE/EN parity holds).

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

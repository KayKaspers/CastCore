# CastCore — Security

Security is built in from the start, not bolted on.

## Authentication & sessions
- Username/password login; passwords hashed with **argon2id**.
- **JWT** access tokens (short TTL) + **refresh** tokens (rotating, stored hashed in
  `sessions`, revocable). Logout revokes the refresh token. Active sessions are listable and
  individually revocable; the current device is flagged via a session-id (`sid`) claim.
- **API tokens** for automation — sent as `Authorization: Bearer cc_…`, hashed at rest,
  authenticate as their owner; the `cc_` prefix disambiguates them from JWTs.
- **2FA (TOTP)** — implemented: per-user setup/verify/disable, enforced at login, with an
  admin reset. The TOTP secret is stored encrypted.

## Authorization (RBAC)
| Role | Capabilities |
| --- | --- |
| **Admin** | Everything: users, settings, updates, backups, all streams/sources/platforms |
| **Operator** | Create/run/manage streams, channels, sources, platforms, recordings; no user/system admin |
| **Viewer** | Read-only: dashboards, monitoring, logs, status |

Every endpoint declares the required role; checks are enforced server-side.

## Secret handling
- Encrypted at rest with **Fernet** (`ENCRYPTION_KEY` from env, never in DB/repo):
  stream keys, platform API keys, OAuth **refresh tokens**, SMB/NFS/cloud credentials,
  notification secrets.
- **Write-only** over the API: accepted on save, returned **masked** (`••••1234`).
- **Never logged.** Command previews and FFmpeg logs mask secrets (stream keys in URLs,
  passwords) before display/storage.

## Transport & web
- HTTPS enforced via reverse proxy (Caddy auto-cert / Nginx).
- The API is **Bearer-token based** (no cookie login), so cookie-CSRF does not apply; no
  dedicated CSRF token is used.
- **Rate limiting** (implemented): Redis-backed throttling on sensitive auth endpoints
  (`login`, `refresh`, `2fa/verify`, token creation, `setup/admin`) → `429 auth.rate_limited`.
  See the admin security guide for configuration. Broader per-endpoint limits are still TODO.
- Security headers (implemented at the reverse proxy): **HSTS**, `X-Content-Type-Options`,
  `Referrer-Policy`. **CSP is not yet set** (TODO).

## FFmpeg & system safety (critical)
- **No shell execution.** FFmpeg/ffprobe/mount/rclone invoked with **argument lists**
  via `subprocess`/asyncio (`shell=False`). No string interpolation into shells.
- **FFmpeg decoder CVEs (e.g. CVE-2026-8461 / MagicYUV):** the installed FFmpeg/ffprobe
  version is detected at runtime and **a build < 8.1.2 is flagged as vulnerable** (system
  status, preflight, setup). A **safe-media mode** flags/blocks risky codecs (default
  blocklist: `magicyuv`). See [FFmpeg requirements](en/admin-guide/ffmpeg-requirements.md).
  *Note: a patched FFmpeg ≥ 8.1.2 is not yet the verified default binary — see that page.*
- **Minimal process environment:** spawned FFmpeg processes get no CastCore secrets in their
  environment (SECRET_KEY/ENCRYPTION_KEY/DB creds are stripped).
- **Path traversal prevention:** all file/media/mount/recording paths validated and
  confined to configured roots (`MEDIA_DIR`, `MOUNT_DIR`, `RECORDINGS_DIR`, …).
- **Safe uploads:** thumbnails/assets validated by type + size, stored with sanitized,
  generated filenames; no execution; served with safe content types.
- **Mount credentials** written to restrictive cred files (`0600`, owned by `castcore`),
  never passed on the command line where they'd appear in process listings.

## Auditing & operations
- **Audit log** for security-relevant actions (login, role change, secret update,
  start/stop, backup/restore, update) with actor, target, IP, timestamp.
- Restrictive file permissions on data/log/config directories; dedicated unprivileged
  system user `castcore` for native installs.
- **Container hardening:** `no-new-privileges` on backend/process-manager/worker; the
  **worker** (which processes untrusted media) additionally `cap_drop: ALL` and runs
  **non-root**. The **backend and process-manager still run as root** (optional in-container
  CIFS/NFS mounts need `SYS_ADMIN`; prefer host-side mounts) — full non-root is a known gap.

## Status (implemented vs. gaps)
Implemented: argon2id · JWT rotation + revocation · RBAC on every route · 2FA · API tokens ·
session management · **rate limiting** (auth endpoints) · Fernet encryption for secret
columns · secrets masked in UI & logs · `shell=False` everywhere · path confinement · upload
validation · audit log · restrictive file perms · FFmpeg version detection + safe-media mode.

Known gaps: **CSP** header not set (CSRF N/A — Bearer API); broader (non-auth) rate limits;
patched **FFmpeg ≥ 8.1.2** not yet the verified default; backend/process-manager not yet
non-root; OAuth **metadata push** not implemented; no frontend/migration tests.

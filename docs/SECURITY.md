# CastCore — Security

Security is built in from the start, not bolted on.

## Authentication & sessions
- Username/password login; passwords hashed with **argon2id**.
- **JWT** access tokens (short TTL) + **refresh** tokens (rotating, stored hashed in
  `sessions`, revocable). Logout revokes the refresh token.
- **API tokens** for automation (`X-API-Key`), scoped, hashed at rest.
- Optional **2FA (TOTP)** — Phase 4; `users.totp_secret` stored encrypted.

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
- Principle of least privilege for container capabilities (only add `SYS_ADMIN`/
  `/dev/fuse` when in-container mounting is explicitly enabled).

## Checklist (implementation gate)
- [ ] argon2id hashing · [ ] JWT rotation + revocation · [ ] RBAC on every route
- [ ] Fernet encryption for all secret columns · [ ] secrets masked in UI & logs
- [ ] shell=False everywhere · [ ] path confinement · [ ] upload validation
- [ ] rate limiting · [ ] CSRF/XSS/CSP · [ ] audit log · [ ] restrictive file perms

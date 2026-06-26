---
title: "Security best practices"
description: "Hardening, roles, secrets, safe uploads, audit."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-26
---

# Security best practices

> Security is built into CastCore from the start. This page summarizes the key measures
> for secure operation.

**Audience:** administrators.

## Authentication & roles

- Passwords are hashed with **argon2id**.
- **JWT** access tokens (short-lived) + rotating, revocable refresh tokens.
- Roles **Admin / Operator / Viewer** – enforced server-side
  ([Roles](/docs/en/reference/roles.md)).
- Optional **two-factor authentication (2FA / TOTP)** per user.

## Two-factor authentication (2FA)

CastCore supports time-based one-time codes (**TOTP**, RFC 6238), compatible with common
authenticator apps (Google Authenticator, Aegis, 1Password, …).

**Set up** (each user for their own account, under **Settings → Profile**):

1. Choose **Set up 2FA**. CastCore generates secret key material.
2. Add the shown `otpauth://` link or the manual key to your authenticator app.
3. Enter a current 6-digit code and click **Activate**. Only then is 2FA active.

**Sign-in:** when 2FA is enabled, CastCore asks for the current code in addition to
username and password.

**Disable:** under **Settings → Profile** by entering a valid code – this prevents an
accidental or unauthorized shutdown of 2FA.

> 🔐 The TOTP secret is stored **encrypted at-rest** like all secrets (Fernet,
> `ENCRYPTION_KEY`) and never returned in clear text.
>
> ⚠️ If the second factor is lost, an **admin** can reset 2FA for the affected user:
> **User management** (`/users`) → the user's row → **Reset 2FA**. The user then signs in
> with a password only again and can set up 2FA anew if needed. Also keep your app's
> backup codes safe.

See also: [Settings](/docs/en/user-guide/settings.md).

## Secrets

- At-rest encryption with **Fernet** (`ENCRYPTION_KEY` from the environment): stream keys,
  platform tokens, OAuth refresh tokens, SMB passwords, notification secrets.
- Secrets are **write-only** over the API and returned **masked**.
- **Never logged.** Command previews mask stream keys in URLs.
- Details: [Secrets management](/docs/en/admin-guide/secrets.md).

## Transport & web

- HTTPS via the reverse proxy ([HTTPS](/docs/en/admin-guide/https.md)).
- Security headers at the reverse proxy: **HSTS**, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy` (Caddy/nginx). A **CSP** header is currently **not** set.
- The API is **Bearer-token based** (no cookie login), so classic cookie-CSRF attacks do not
  apply; there is deliberately no dedicated CSRF token.

## Rate limiting

Sensitive auth endpoints are **throttled** (Redis-backed, fixed window):
`POST /auth/login`, `/auth/refresh`, `/auth/2fa/verify`, `/tokens` (creation) and
`/setup/admin`. Per client IP the default is **10 attempts per 300 s**; beyond that the API
responds `429` with the translatable code `auth.rate_limited` (plus a `Retry-After` header).

- Configurable via `RATE_LIMIT_ENABLED`, `RATE_LIMIT_AUTH_ATTEMPTS`,
  `RATE_LIMIT_AUTH_WINDOW_SECONDS` ([environment variables](/docs/en/reference/environment-variables.md)).
- The client IP is taken from the first `X-Forwarded-For` hop – a correctly configured
  reverse proxy is therefore required.
- **Fail-open:** if Redis is unreachable, requests are **not** blocked (no accidental
  lockout). For extra hardening the reverse proxy can throttle too (Caddy `rate_limit` or
  nginx `limit_req`).

## System & FFmpeg

- **No shell execution**: FFmpeg/ffprobe/mount run with argument lists.
- **Path-traversal protection**: all paths confined to configured roots.
- **Safe uploads**: type/size validation, generated filenames.
- Mount credentials in restrictive `0600` files.
- **Minimal process environment**: spawned FFmpeg processes receive **no** CastCore secrets
  (SECRET_KEY/ENCRYPTION_KEY/DB credentials) in their environment.
- **Container hardening**: `no-new-privileges` for all app services; the worker (which
  processes potentially untrusted media) additionally `cap_drop: ALL` and runs **non-root**.

## FFmpeg decoder security (CVE-2026-8461 / MagicYUV)

FFmpeg decodes foreign media, so its version is security-relevant. CastCore detects the
installed FFmpeg/ffprobe version, **warns on versions < 8.1.2**, and treats risky codecs (e.g.
MagicYUV) specially (safe-media mode, preflight block, media badge). Details and patch paths:
[FFmpeg requirements & security](/docs/en/admin-guide/ffmpeg-requirements.md).

## Audit log

CastCore records security-relevant actions in the **audit log** (UI: `/audit`, admin
only). Captured events include: **login**, **stream start/stop/restart**, **backup
create/restore**, **user create/delete** – each with actor, action, target, IP and
timestamp.

> 🔐 The audit log is **excluded from backup/restore** – it survives a restore and stays
> accountable.

## Checklist

- [ ] `SECRET_KEY` and `ENCRYPTION_KEY` set uniquely and backed up
- [ ] HTTPS active, valid certificate
- [ ] Only required ports published
- [ ] Backups configured and tested ([Backup & restore](/docs/en/user-guide/backup-restore.md))
- [ ] Roles granted sparingly

## Related pages

- [Secrets management](/docs/en/admin-guide/secrets.md)
- [Roles](/docs/en/reference/roles.md)
- [Backup & restore](/docs/en/user-guide/backup-restore.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

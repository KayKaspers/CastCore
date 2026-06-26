---
title: "Security best practices"
description: "Hardening, roles, secrets, safe uploads, audit."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-25
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
- CSRF/XSS protection, rate limiting, security headers (CSP, HSTS).

## System & FFmpeg

- **No shell execution**: FFmpeg/ffprobe/mount run with argument lists.
- **Path-traversal protection**: all paths confined to configured roots.
- **Safe uploads**: type/size validation, generated filenames.
- Mount credentials in restrictive `0600` files.

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
_Last reviewed: 2026-06-25 · Status: stable_

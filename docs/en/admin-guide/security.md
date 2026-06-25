---
title: "Security best practices"
description: "Hardening, roles, secrets, safe uploads, audit."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
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
- Optional **2FA (TOTP)** prepared.

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
_Last reviewed: 2026-06-24 · Status: stable_

---
title: "Secrets management"
description: "Encryption (Fernet), ENCRYPTION_KEY, key rotation."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Secrets management

> CastCore stores sensitive data (stream keys, SMB/OAuth credentials, notification
> secrets) **encrypted**.

**Audience:** administrators.

## Keys

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Signs JWT tokens. 64 hex chars. |
| `ENCRYPTION_KEY` | **Fernet key** to encrypt stored secrets. |

Generate:
```bash
openssl rand -hex 32                     # SECRET_KEY
openssl rand -base64 32 | tr '+/' '-_'   # ENCRYPTION_KEY (valid Fernet key)
```

## Properties

- Secrets are encrypted **at rest** with Fernet.
- Over the API they are **write-only**: accepted on input, **masked** on output
  (e.g. `••••1234`) or shown only as "present".
- Secrets **never** appear in logs; command previews mask stream keys in URLs.

## Important: keep the ENCRYPTION_KEY safe

> 🔐 **Without the `ENCRYPTION_KEY`, encrypted data is unusable.** Keep it safe **and
> separate** from the backups. A logical backup contains secrets only **encrypted** –
> restoring requires the same key.

## Key rotation

Changing the `ENCRYPTION_KEY` makes existing encrypted values unreadable. Plan a rotation
only together with re-encrypting the affected fields (future tooling).

## Related pages

- [Security best practices](/docs/en/admin-guide/security.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

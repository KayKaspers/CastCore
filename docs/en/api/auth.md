---
title: "API: auth"
description: "Login, JWT refresh, logout, API tokens."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API: auth

> Authentication via JWT (access + rotating refresh).

**Audience:** developers / integrators.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Sign in → `access_token`, `refresh_token`, `user` |
| `POST` | `/api/v1/auth/refresh` | New token pair from a refresh token |
| `POST` | `/api/v1/auth/logout` | Revoke own sessions |
| `GET` | `/api/v1/auth/me` | Current profile |

## Example: login

```bash
curl -k -X POST https://<host>/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"username":"admin","password":"<secret>"}'
```

Response:
```json
{ "access_token": "…", "refresh_token": "…", "token_type": "bearer", "user": { … } }
```

## Using the token

```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer <access_token>'
```

## Notes

- Access token short-lived (`ACCESS_TOKEN_TTL_MINUTES`), refresh rotates and is revocable.
- Passwords are hashed with **argon2id**.

## Related pages

- [Roles](/docs/en/reference/roles.md) · [Security](/docs/en/admin-guide/security.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

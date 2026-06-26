---
title: "API: auth"
description: "Login, JWT refresh, logout, API tokens."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-26
---

# API: auth

> Authentication via JWT (access + rotating refresh).

**Audience:** developers / integrators.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Sign in → `access_token`, `refresh_token`, `user` (optional `totp_code`) |
| `POST` | `/api/v1/auth/refresh` | New token pair from a refresh token |
| `POST` | `/api/v1/auth/logout` | Revoke own sessions |
| `GET` | `/api/v1/auth/me` | Current profile |
| `POST` | `/api/v1/auth/2fa/setup` | Set up 2FA → `secret`, `otpauth_uri` |
| `POST` | `/api/v1/auth/2fa/verify` | Activate 2FA (body `{ "code": "123456" }`) |
| `POST` | `/api/v1/auth/2fa/disable` | Disable 2FA (valid code required) |
| `GET` | `/api/v1/tokens` | List your API tokens |
| `POST` | `/api/v1/tokens` | Create an API token → `token` (once only) |
| `DELETE` | `/api/v1/tokens/{id}` | Revoke an API token |
| `GET` | `/api/v1/auth/sessions` | Your active sessions (`current` flags this one) |
| `DELETE` | `/api/v1/auth/sessions/{id}` | Sign out a single session |
| `POST` | `/api/v1/auth/sessions/revoke-others` | Sign out all sessions except the current one |

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

If the account has **2FA** enabled, `/login` without `totp_code` responds `401` with the
error code `auth.totp_required`; a wrong code gives `auth.totp_invalid`. Retry the login
with `"totp_code":"123456"`.

## Using the token

```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer <access_token>'
```

## Personal API tokens

For non-interactive clients (scripts, CI) create a long-lived **personal access token** –
in the UI under **Settings → API tokens** or via the API:

```bash
curl -k -X POST https://<host>/api/v1/tokens \
  -H 'authorization: Bearer <access_token>' \
  -H 'content-type: application/json' \
  -d '{"name":"ci-bot","expires_in_days":90}'
```

Response (the plaintext token is shown **only once**):
```json
{ "id": "…", "name": "ci-bot", "token": "cc_…", "expires_at": "…", "created_at": "…" }
```

Use the token like an access token:
```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer cc_…'
```

- Tokens carry the `cc_` prefix and act with **their owner's permissions**.
- They are stored **hashed only**; the plaintext is not recoverable.
- `expires_in_days` is optional (omit for non-expiring). Revoke any time via
  `DELETE /api/v1/tokens/{id}`.

## Sessions

Each sign-in creates a **session** (bound to the refresh token, with user-agent/IP). The
access token carries the session id (`sid`) so the current session can be flagged. In the
UI: **Settings → Active sessions**.

```bash
curl -k https://<host>/api/v1/auth/sessions -H 'authorization: Bearer <access_token>'
```

Sign out a single session with `DELETE /api/v1/auth/sessions/{id}`; all but the current one
with `POST /api/v1/auth/sessions/revoke-others`. (API tokens have no `sid`, so none counts as
the "current" session.)

## Notes

- Access token short-lived (`ACCESS_TOKEN_TTL_MINUTES`), refresh rotates and is revocable.
- Passwords are hashed with **argon2id**.
- Treat API tokens like passwords – never commit them to repos/logs.
- **Rate limiting:** `login`, `refresh`, `2fa/verify` and token creation are throttled. On
  exceeding the limit the API responds `429` with code `auth.rate_limited` (plus a
  `Retry-After` header). Details: [Security](/docs/en/admin-guide/security.md#rate-limiting).

## Related pages

- [Roles](/docs/en/reference/roles.md) · [Security](/docs/en/admin-guide/security.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

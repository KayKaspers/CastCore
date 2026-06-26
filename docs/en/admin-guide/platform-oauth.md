---
title: "Platform OAuth (YouTube/Twitch)"
description: "Connect YouTube/Twitch accounts via OAuth, store tokens securely."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-25
---

# Platform OAuth (YouTube/Twitch)

> OAuth links real **platform accounts** to CastCore. Access tokens are stored **encrypted**
> and let CastCore set stream metadata on your behalf. The integration is optional and
> per-provider.

**Audience:** administrators.

## Overview

A platform is **enabled** once its client id is configured **and** a `PUBLIC_BASE_URL` is
set. Otherwise it shows as "not configured" in the UI.

| Provider | Authorization | Default scope |
| --- | --- | --- |
| `youtube` | Google OAuth (`accounts.google.com`) | `…/auth/youtube` |
| `twitch` | Twitch (`id.twitch.tv`) | `channel:manage:broadcast` |

## Setup

1. **Register an OAuth app** with the provider (Google Cloud Console or Twitch Developer
   Console) and create a client id + secret.
2. **Add the redirect URI** at the provider exactly as:
   ```text
   https://<your-host>/api/v1/oauth/<provider>/callback
   ```
   e.g. `https://stream.example.com/api/v1/oauth/twitch/callback`.
3. Set in `.env`:
   ```ini
   PUBLIC_BASE_URL=https://stream.example.com
   TWITCH_CLIENT_ID=…
   TWITCH_CLIENT_SECRET=…
   # and/or
   YOUTUBE_CLIENT_ID=…
   YOUTUBE_CLIENT_SECRET=…
   ```
4. Restart the backend. Under **Platforms** (`/resources`) a **Connect** button appears.

## Connect an account

1. Click **Connect** – CastCore redirects to the provider.
2. Approve access at the provider. It redirects back to the callback URL.
3. CastCore exchanges the code for tokens, stores them encrypted, and shows the account
   under **Linked accounts**. You can disconnect at any time.

## Security

> 🔐 Access and refresh tokens are stored **Fernet-encrypted** (`ENCRYPTION_KEY`) and are
> **never** returned via the API. The OAuth `state` is a short-lived signed token (10 min)
> that carries the initiating user and prevents CSRF. Keep client secrets in `.env`, not in
> the repository.

## Troubleshooting

- **No "Connect" button**: are `PUBLIC_BASE_URL` and the client id set? Backend restarted?
- **"Connection failed"** after returning: the provider's redirect URI must match exactly
  (scheme, host, path). Is the secret correct? Is the clock in sync (state TTL)?

## Related pages

- [Platforms & metadata](/docs/en/user-guide/platforms.md)
- [Security best practices](/docs/en/admin-guide/security.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-25 · Status: stable_

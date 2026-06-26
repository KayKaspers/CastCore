---
title: "Settings"
description: "General settings, notifications and the scheduler."
lang: en
audience: "Users / Administrators"
status: stable
lastReviewed: 2026-06-25
---

# Settings

> Under settings you manage, among other things, **notifications** and the **scheduler**.
> System-level values are set via environment variables
> ([Environment variables](/docs/en/reference/environment-variables.md)).

**Audience:** users / administrators. UI area: **Settings** (`/settings`).

## My profile & language

Under **My profile** you choose your **language** (German/English). The choice is **saved
per user** and applies after signing in again on other devices (not just locally in the
browser).

## Two-factor authentication (2FA)

In **My profile** you can enable 2FA via an **authenticator app** (TOTP):

1. Click **Set up 2FA** – CastCore shows an `otpauth://` link and a manual key.
2. Add both to your app, then enter a **6-digit code** and click **Activate**.
3. From now on, sign-in additionally asks for this code.

To **disable**, enter a valid code again. Details and recovery notes:
[Security best practices](/docs/en/admin-guide/security.md#two-factor-authentication-2fa).

## API tokens

Under **Settings → API tokens** you create personal access tokens for the API (e.g. for
scripts or CI). Give a **name** and optionally a **validity in days**. The plaintext token
is shown **only once** – copy it immediately and store it safely. Tokens act with **your**
permissions and can be **revoked** any time. Usage and examples:
[API: auth](/docs/en/api/auth.md).

## Instance settings (admin)

Administrators set the **instance name** and the **default language** for new users.

## Notifications

UI area: **Notifications** (`/notifications`). Create channels and subscribe to events.
Connection details are stored **encrypted** (write-only).

### Channels

| Channel | Required fields |
| --- | --- |
| **Webhook** | `url` |
| **Discord** | `url` (webhook URL) |
| **Slack** | `url` (incoming webhook) |
| **Gotify** | `url`, `token` |
| **Telegram** | `bot_token`, `chat_id` |
| **Email** | `host`, `port`, `from`, `to`, optional `username`/`password` |

### Events

| Event | When |
| --- | --- |
| `stream_started` / `stream_stopped` / `stream_failed` | A stream status change (via the status consumer). |
| `source_offline` | A source **test** fails. |
| `preflight_failed` | A preflight check is **red**. |
| `backup_done` | A backup was created (manual or scheduled). |
| `test` | Triggered manually via **Test**. |

> 💡 Use **Test** to verify a channel immediately, without waiting for a real event.

## Scheduler

UI area: **Scheduler** (`/scheduler`). Time-based / recurring actions:

- **Types:** once, interval (minutes), daily (HH:MM **UTC**).
- **Actions:** `stream_start`, `stream_stop`, `backup`, `scan`.
- Per entry: next run, last status, **run** (run now).

A background loop in the backend runs due entries about every 20 seconds.

## Notes

> 🔐 Notification secrets and SMTP passwords are stored encrypted and shown externally
> only as "present". See [Secrets](/docs/en/admin-guide/secrets.md).

## Related pages

- [Users & roles](/docs/en/user-guide/users-roles.md)
- [Backup & restore](/docs/en/user-guide/backup-restore.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-25 · Status: stable_

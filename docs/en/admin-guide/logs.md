---
title: "Logs"
description: "Where CastCore logs live and how to read them."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Logs

> CastCore offers several log levels: service logs, live FFmpeg logs and the audit log.

**Audience:** administrators.

## Service logs (Docker)

```bash
docker compose logs -f backend            # API + background loops
docker compose logs -f process-manager    # FFmpeg supervisor
docker compose logs -f worker             # async jobs
docker compose logs -f caddy postgres redis
```

## Service logs (native)

```bash
journalctl -u castcore-backend -f
journalctl -u castcore-process-manager -f
```
Additionally: `/var/log/castcore` (native) or `/data/logs` (data volume).

## Live FFmpeg logs

Per stream job in the UI via **Live logs** – including plain-language hints (stream health
assistant) and a link to the matching [error help](/docs/en/troubleshooting/ffmpeg-errors.md).

## Audit log

Security-relevant actions (login, start/stop, backup, users) are under `/audit`. See
[Security](/docs/en/admin-guide/security.md).

## Notes

> 🔐 Logs contain **no** secrets; stream keys are masked.

## Related pages

- [Monitoring](/docs/en/user-guide/monitoring.md)
- [Troubleshooting](/docs/en/troubleshooting/index.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

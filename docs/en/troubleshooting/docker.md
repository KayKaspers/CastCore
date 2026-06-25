---
title: "Docker problems"
description: "Containers won't start, DB/Redis unreachable."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Docker problems

> Help when the stack doesn't come up cleanly.

**Audience:** administrators.

## Symptom: container restarts / "unhealthy"

**Diagnosis:**
```bash
docker compose ps
docker compose logs --tail=50 <service>
```
**Common causes:**

| Cause | Fix |
| --- | --- |
| Incomplete `.env` | Set `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_PASSWORD` |
| Backend waiting for DB | Until `postgres` is healthy; check logs |
| Port 80/443 in use | Stop the other service or change ports |

## Symptom: database unreachable

**Diagnosis:** `docker compose logs postgres` and `docker compose exec backend python -c "import socket;socket.create_connection(('postgres',5432),2)"`.
**Fix:** keep the password in `.env` consistent; wait for `postgres` healthy.

## Symptom: Redis unreachable

The control channel/status depend on it. `docker compose logs redis`, check the healthcheck.

## Symptom: migrations fail

The backend log shows an Alembic error. For a fresh DB: check the volume; for an upgrade,
create a [backup](/docs/en/user-guide/backup-restore.md) first.

## Reverse proxy / HTTPS

Caddy parse error or no certificate → [HTTPS](/docs/en/admin-guide/https.md) and
[Reverse proxy](/docs/en/admin-guide/reverse-proxy.md).

## Start over (caution: deletes data)

```bash
docker compose down -v && docker compose up -d --build
```

## Related pages

- [Operating with Docker Compose](/docs/en/admin-guide/docker-compose.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

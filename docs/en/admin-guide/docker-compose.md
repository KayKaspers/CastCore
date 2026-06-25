---
title: "Operating with Docker Compose"
description: "Services, volumes, healthchecks and profiles of the compose file."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Operating with Docker Compose

> Everything you need to run the stack with `docker-compose.yml`.

**Audience:** administrators.

## Key commands

```bash
docker compose up -d --build     # build + start
docker compose ps                # status / health
docker compose logs -f backend process-manager   # follow logs
docker compose restart backend   # restart a single service
docker compose down              # stop (keeps data volumes)
docker compose down -v           # stop + DELETE all data volumes
```

## Profiles (optional)

```bash
docker compose --profile mediamtx up -d     # MediaMTX media router
docker compose --profile monitoring up -d   # monitoring exporters
```

## Persistent volumes

| Volume | Content |
| --- | --- |
| `castcore_pg` | PostgreSQL data |
| `castcore_redis` | Redis persistence |
| `castcore_data` | media, recordings, logs, backups, mounts, thumbnails (`/data`) |
| `castcore_caddy_data`/`_config` | certificates / Caddy config |

## Healthchecks & restart

Every service has `restart: unless-stopped` and a healthcheck. `backend`,
`process-manager` and `worker` wait until `postgres`/`redis` are healthy. The backend runs
`alembic upgrade head` automatically on start.

## Migrations

Automatic on backend start. Manually:
```bash
docker compose exec backend alembic upgrade head
```

## Backing up a running stack

Back up the data volume or create a logical backup via the UI / `/api/v1/backups`. See
[Backup & restore](/docs/en/user-guide/backup-restore.md).

## Related pages

- [Install with Docker](/docs/en/getting-started/installation-docker.md)
- [Environment variables](/docs/en/reference/environment-variables.md)
- [Docker problems](/docs/en/troubleshooting/docker.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

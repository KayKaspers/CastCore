---
title: "Docker-Compose-Betrieb"
description: "Services, Volumes, Healthchecks und Profile der Compose-Datei."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Docker-Compose-Betrieb

> Alles Wichtige zum Betrieb des Stacks mit `docker-compose.yml`.

**Zielgruppe:** Administratoren.

## Wichtige Befehle

```bash
docker compose up -d --build     # bauen + starten
docker compose ps                # Status / Health
docker compose logs -f backend process-manager   # Logs folgen
docker compose restart backend   # einzelnen Dienst neu starten
docker compose down              # stoppen (Daten-Volumes bleiben)
docker compose down -v           # stoppen + ALLE Daten-Volumes löschen
```

## Profile (optional)

```bash
docker compose --profile mediamtx up -d     # MediaMTX Media-Router
docker compose --profile monitoring up -d   # Monitoring-Exporter
```

## Persistente Volumes

| Volume | Inhalt |
| --- | --- |
| `castcore_pg` | PostgreSQL-Daten |
| `castcore_redis` | Redis-Persistenz |
| `castcore_data` | Medien, Recordings, Logs, Backups, Mounts, Thumbnails (`/data`) |
| `castcore_caddy_data`/`_config` | Zertifikate / Caddy-Konfiguration |

## Healthchecks & Restart

Jeder Dienst hat `restart: unless-stopped` und einen Healthcheck. `backend`,
`process-manager` und `worker` warten, bis `postgres`/`redis` „healthy" sind. Das Backend
führt beim Start automatisch `alembic upgrade head` aus.

## Migrationen

Automatisch beim Backend-Start. Manuell:
```bash
docker compose exec backend alembic upgrade head
```

## Backup eines laufenden Stacks

Daten-Volume sichern oder ein logisches Backup über die UI/`/api/v1/backups` erstellen.
Siehe [Backup & Restore](/docs/de/user-guide/backup-restore.md).

## Verwandte Seiten

- [Installation mit Docker](/docs/de/getting-started/installation-docker.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)
- [Docker-Probleme](/docs/de/troubleshooting/docker.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Docker-Probleme"
description: "Container starten nicht, DB/Redis nicht erreichbar."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Docker-Probleme

> Hilfe, wenn der Stack nicht sauber hochkommt.

**Zielgruppe:** Administratoren.

## Symptom: Container startet neu / „unhealthy"

**Diagnose:**
```bash
docker compose ps
docker compose logs --tail=50 <dienst>
```
**Häufige Ursachen:**

| Ursache | Lösung |
| --- | --- |
| `.env` unvollständig | `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_PASSWORD` setzen |
| Backend wartet auf DB | Bis `postgres` „healthy" ist; Logs prüfen |
| Port 80/443 belegt | Anderen Dienst stoppen oder Ports anpassen |

## Symptom: Datenbank nicht erreichbar

**Diagnose:** `docker compose logs postgres` und `docker compose exec backend python -c "import socket;socket.create_connection(('postgres',5432),2)"`.
**Lösung:** Passwort in `.env` konsistent; `postgres` healthy abwarten.

## Symptom: Redis nicht erreichbar

Steuerkanal/Status hängen davon ab. `docker compose logs redis`, Healthcheck prüfen.

## Symptom: Migrationen schlagen fehl

Backend-Log zeigt Alembic-Fehler. Bei frischer DB: Volume prüfen; bei Upgrade vorher
[Backup](/docs/de/user-guide/backup-restore.md) erstellen.

## Reverse-Proxy / HTTPS

Caddy-Parsefehler oder kein Zertifikat → [HTTPS](/docs/de/admin-guide/https.md) und
[Reverse Proxy](/docs/de/admin-guide/reverse-proxy.md).

## Neustart von vorn (Achtung: löscht Daten)

```bash
docker compose down -v && docker compose up -d --build
```

## Verwandte Seiten

- [Docker-Compose-Betrieb](/docs/de/admin-guide/docker-compose.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-24 · Status: Stabil_

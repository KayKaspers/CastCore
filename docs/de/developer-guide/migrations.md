---
title: "Migrationen"
description: "Alembic-Migrationen erstellen und anwenden."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Migrationen

> Schemaänderungen laufen über **Alembic** (`backend/migrations/`).

**Zielgruppe:** Entwickler.

## Anwenden

Im Docker-Betrieb **automatisch** beim Backend-Start. Manuell:

```bash
docker compose exec backend alembic upgrade head
```

## Neue Migration erstellen

1. Modell in `app/models/` ändern und in `app/models/__init__.py` registrieren.
2. Migration generieren (Autogenerate) oder von Hand schreiben:
   ```bash
   docker compose exec backend alembic revision -m "beschreibung" --autogenerate
   ```
3. Datei in `backend/migrations/versions/` prüfen/anpassen (UUID-Spalten, Defaults,
   Indizes) und die `down_revision` korrekt verketten.

## Konventionen

- Dateiname/Revision fortlaufend nummeriert (z. B. `0014_…`).
- `sa.Uuid()` für UUID-PKs/FKs, `sa.JSON()` für JSON-Spalten.
- Server-Defaults für Bool/JSON setzen (`server_default`), damit bestehende Zeilen passen.

## Status prüfen

Aktuelle vs. neueste Revision: **Updates**-Seite (`/api/v1/update/state`).

## Verwandte Seiten

- [Datenbank](/docs/de/developer-guide/database.md) · [Updates](/docs/de/user-guide/updates.md)

---
_Stand: 2026-06-24 · Status: Stabil_

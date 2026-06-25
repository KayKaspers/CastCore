---
title: "Updates"
description: "CastCore aktualisieren (Docker und nativ)."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Updates

> Die **Updates**-Seite (`/updates`, nur Admin) zeigt die laufende Version, den
> Deployment-Modus und den **Migrationsstatus** der Datenbank.

**Zielgruppe:** Administratoren.

## Was die Seite zeigt

| Feld | Bedeutung |
| --- | --- |
| **Version** | Laufende CastCore-Version. |
| **Environment** | `production` / `development`. |
| **Deployment** | `docker` oder `native` (automatisch erkannt). |
| **DB-Revision / Head-Revision** | Aktuelle bzw. neueste Alembic-Migration. |
| **Schema aktuell** | Ob die Datenbank auf dem neuesten Stand ist. |

## Aktualisieren mit Docker

```bash
git pull
docker compose pull        # falls vorgefertigte Images genutzt werden
docker compose up -d --build
```

Das Backend führt **Migrationen automatisch** beim Start aus
([Installation mit Docker](/docs/de/getting-started/installation-docker.md)).

## Native Aktualisierung

```bash
sudo ./scripts/update.sh
```

`update.sh` legt **vor** dem Update ein Backup an, aktualisiert den Code, wendet
Migrationen an und startet die Dienste neu.

## Vor jedem Update

> ⚠️ **Backup empfohlen.** Erstelle vorher ein [Backup](/docs/de/user-guide/backup-restore.md).
> Bei Problemen ist der Rollback = das Backup vor dem Update wiederherstellen.

## Hinweise

> 💡 Steht „Migrationen: ausstehend", werden sie beim nächsten Docker-Start automatisch
> angewendet; nativ über `update.sh`.

## Verwandte Seiten

- [Backup & Restore](/docs/de/user-guide/backup-restore.md)
- [Installation mit Docker](/docs/de/getting-started/installation-docker.md)
- [Migrationen (Entwickler)](/docs/de/developer-guide/migrations.md)

---
_Stand: 2026-06-24 · Status: Stabil_

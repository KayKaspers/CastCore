---
title: "Rollen"
description: "Admin, Operator, Viewer im Detail."
lang: de
audience: "Alle Rollen"
status: stable
lastReviewed: 2026-06-24
---

# Rollen

> CastCore nutzt rollenbasierte Zugriffskontrolle (RBAC). Jede API-Route verlangt eine
> bestimmte Rolle; **Admin** darf immer alles.

**Zielgruppe:** Alle Rollen.

## Die drei Rollen

| Rolle | Darf … |
| --- | --- |
| **Admin** | Alles: Benutzer, Einstellungen, Updates, Backups, Benachrichtigungen sowie alle Streams/Quellen/Plattformen |
| **Operator** | Streams, Channels, Quellen, Plattformen, Recordings anlegen/steuern; **keine** Benutzer-/Systemverwaltung |
| **Viewer** | Nur Lesen: Dashboards, Monitoring, Logs, Status |

## Wie wird geprüft?

Die Prüfung erfolgt **serverseitig** für jede Route. Ein fehlender Anspruch führt zu
HTTP `403` mit dem übersetzbaren Code `auth.forbidden`.

## Verwandte Seiten

- [Benutzer & Rollen](/docs/de/user-guide/users-roles.md)
- [Berechtigungen](/docs/de/reference/permissions.md)
- [Security Best Practices](/docs/de/admin-guide/security.md)

---
_Stand: 2026-06-24 · Status: Stabil_

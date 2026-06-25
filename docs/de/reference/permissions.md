---
title: "Berechtigungen"
description: "Welche Aktion welche Rolle erfordert."
lang: de
audience: "Alle Rollen"
status: stable
lastReviewed: 2026-06-24
---

# Berechtigungen

> Übersicht, welche Rolle welche Bereiche nutzen darf. **Admin** darf immer alles.

**Zielgruppe:** Alle Rollen. Siehe auch [Rollen](/docs/de/reference/roles.md).

## Matrix (Auszug)

| Bereich | Viewer | Operator | Admin |
| --- | :---: | :---: | :---: |
| Dashboard / Monitoring / Logs (lesen) | ✅ | ✅ | ✅ |
| Stream-Jobs / Channels / Quellen / Profile / Ziele | – | ✅ | ✅ |
| Medienbibliothek / Playlists / Recordings | – | ✅ | ✅ |
| Plattform-Metadaten / Assets | – | ✅ | ✅ |
| Benutzerverwaltung | – | – | ✅ |
| Einstellungen (Instanz) | – | – | ✅ |
| Benachrichtigungen | – | – | ✅ |
| Backup / Restore | – | – | ✅ |
| Audit-Log / Updates | – | – | ✅ |

## Durchsetzung

Die Prüfung erfolgt **serverseitig** pro Route. Fehlt der Anspruch → HTTP `403`
(`auth.forbidden`).

## Verwandte Seiten

- [Rollen](/docs/de/reference/roles.md) · [Benutzer & Rollen](/docs/de/user-guide/users-roles.md)

---
_Stand: 2026-06-24 · Status: Stabil_

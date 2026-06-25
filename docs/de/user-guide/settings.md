---
title: "Einstellungen"
description: "Allgemeine Einstellungen, Benachrichtigungen und Scheduler."
lang: de
audience: "Anwender / Administratoren"
status: stable
lastReviewed: 2026-06-25
---

# Einstellungen

> Unter Einstellungen verwaltest du u. a. **Benachrichtigungen** und den **Scheduler**.
> Systemnahe Werte werden über Umgebungsvariablen gesetzt
> ([Umgebungsvariablen](/docs/de/reference/environment-variables.md)).

**Zielgruppe:** Anwender / Administratoren. UI-Bereich: **Einstellungen** (`/settings`).

## Mein Profil & Sprache

Unter **Mein Profil** wählst du deine **Sprache** (Deutsch/Englisch). Die Auswahl wird
**pro Benutzer gespeichert** und gilt auch nach erneuter Anmeldung auf anderen Geräten
(nicht nur lokal im Browser).

## Zwei-Faktor-Authentifizierung (2FA)

Im Bereich **Mein Profil** kannst du 2FA per **Authenticator-App** (TOTP) aktivieren:

1. **2FA einrichten** klicken – CastCore zeigt einen `otpauth://`-Link und einen
   manuellen Schlüssel an.
2. Beides in deiner App hinterlegen, dann einen **6-stelligen Code** eingeben und
   **Aktivieren**.
3. Ab jetzt fragt die Anmeldung zusätzlich nach diesem Code.

Zum **Deaktivieren** gibst du erneut einen gültigen Code ein. Details und Hinweise zur
Wiederherstellung: [Security Best Practices](/docs/de/admin-guide/security.md#zwei-faktor-authentifizierung-2fa).

## Instanz-Einstellungen (Admin)

Administratoren setzen **Instanzname** und **Standardsprache** für neue Benutzer.

## Benachrichtigungen

UI-Bereich: **Benachrichtigungen** (`/notifications`). Lege Kanäle an und abonniere
Events. Verbindungsdaten werden **verschlüsselt** gespeichert (write-only).

### Kanäle

| Kanal | Benötigte Felder |
| --- | --- |
| **Webhook** | `url` |
| **Discord** | `url` (Webhook-URL) |
| **Slack** | `url` (Incoming-Webhook) |
| **Gotify** | `url`, `token` |
| **Telegram** | `bot_token`, `chat_id` |
| **E-Mail** | `host`, `port`, `from`, `to`, optional `username`/`password` |

### Events

| Event | Wann |
| --- | --- |
| `stream_started` / `stream_stopped` / `stream_failed` | Statuswechsel eines Streams (über den Status-Consumer). |
| `source_offline` | Ein Quellen-**Test** schlägt fehl. |
| `preflight_failed` | Ein Preflight-Check ergibt **Rot**. |
| `backup_done` | Ein Backup wurde erstellt (manuell oder geplant). |
| `test` | Über **Test** manuell ausgelöst. |

> 💡 Mit **Test** prüfst du einen Kanal sofort, ohne auf ein echtes Event zu warten.

## Scheduler

UI-Bereich: **Scheduler** (`/scheduler`). Zeitgesteuerte/wiederkehrende Aktionen:

- **Typen:** einmalig, Intervall (Minuten), täglich (HH:MM **UTC**).
- **Aktionen:** `stream_start`, `stream_stop`, `backup`, `scan`.
- Pro Eintrag: nächster Lauf, letzter Status, **run** (Sofort-Ausführung).

Ein Hintergrund-Loop im Backend führt fällige Einträge alle ~20 Sekunden aus.

## Hinweise

> 🔐 Benachrichtigungs-Secrets und SMTP-Passwörter werden verschlüsselt abgelegt und nach
> außen nur als „vorhanden" angezeigt. Siehe [Secrets](/docs/de/admin-guide/secrets.md).

## Verwandte Seiten

- [Benutzer & Rollen](/docs/de/user-guide/users-roles.md)
- [Backup & Restore](/docs/de/user-guide/backup-restore.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-25 · Status: Stabil_

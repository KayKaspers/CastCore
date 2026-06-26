---
title: "Benutzer & Rollen"
description: "Benutzer verwalten und Rollen (Admin/Operator/Viewer) vergeben."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-25
---

# Benutzer & Rollen

> In der **Benutzerverwaltung** (`/users`, nur Admin) legst du Benutzer an, vergibst
> Rollen, setzt Passwörter zurück und aktivierst/deaktivierst Konten.

**Zielgruppe:** Administratoren.

## Benutzer anlegen

1. Im Formular **Benutzername**, **Passwort** (mind. 8 Zeichen), optional **E-Mail** und
   eine **Rolle** angeben.
2. **Erstellen**. Der Benutzer kann sich danach anmelden; seine Sprache lässt sich später
   unter [Einstellungen](/docs/de/user-guide/settings.md) pro Benutzer ändern.

## Rollen ändern

Aktiviere/deaktiviere pro Benutzer die Rollen **admin**, **operator**, **viewer** direkt
in der Tabelle. Mindestens eine Rolle bleibt erhalten. Bedeutung der Rollen:
[Rollen](/docs/de/reference/roles.md).

## Konto aktiv/inaktiv

Über das **Aktiv**-Häkchen sperrst oder entsperrst du ein Konto. Ein **deaktivierter**
Benutzer kann sich nicht anmelden.

## Passwort zurücksetzen

**Passwort zurücksetzen** → neues Passwort (mind. 8 Zeichen) eingeben.

## 2FA zurücksetzen

Die Spalte **2FA** zeigt, ob ein Benutzer die Zwei-Faktor-Authentifizierung aktiviert hat.
Hat ein Benutzer den zweiten Faktor verloren, klickst du **2FA zurücksetzen**. Danach
meldet sich der Benutzer wieder nur mit Passwort an und kann 2FA bei Bedarf neu einrichten.
Mehr zu 2FA: [Einstellungen](/docs/de/user-guide/settings.md) und
[Security Best Practices](/docs/de/admin-guide/security.md#zwei-faktor-authentifizierung-2fa).

## Hinweise

> 🔐 Aktionen wie Anlegen/Löschen und **2FA-Reset** werden im
> [Audit-Log](/docs/de/admin-guide/security.md) protokolliert. Das **eigene** Konto kann
> nicht deaktiviert oder gelöscht werden.

> ⚠️ Passwörter werden mit **argon2id** gehasht und niemals im Klartext gespeichert.

## Verwandte Seiten

- [Rollen](/docs/de/reference/roles.md)
- [Berechtigungen](/docs/de/reference/permissions.md)
- [Security Best Practices](/docs/de/admin-guide/security.md)

---
_Stand: 2026-06-25 · Status: Stabil_

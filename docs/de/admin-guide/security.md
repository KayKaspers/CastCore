---
title: "Security Best Practices"
description: "Härtung, Rollen, Secrets, sichere Uploads, Audit."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Security Best Practices

> Sicherheit ist in CastCore von Anfang an eingebaut. Diese Seite fasst die wichtigsten
> Maßnahmen für den sicheren Betrieb zusammen.

**Zielgruppe:** Administratoren.

## Authentifizierung & Rollen

- Passwörter werden mit **argon2id** gehasht.
- **JWT** Access-Token (kurzlebig) + rotierende, widerrufbare Refresh-Token.
- Rollen **Admin / Operator / Viewer** – serverseitig erzwungen
  ([Rollen](/docs/de/reference/roles.md)).
- Optional **2FA (TOTP)** vorbereitet.

## Secrets

- Verschlüsselung at-rest mit **Fernet** (`ENCRYPTION_KEY` aus der Umgebung):
  Stream-Keys, Plattform-Tokens, OAuth-Refresh-Tokens, SMB-Passwörter,
  Benachrichtigungs-Secrets.
- Secrets sind **write-only** über die API und werden **maskiert** zurückgegeben.
- **Nie im Log.** Command-Vorschauen maskieren Stream-Keys in URLs.
- Details: [Secrets-Verwaltung](/docs/de/admin-guide/secrets.md).

## Transport & Web

- HTTPS über den Reverse Proxy ([HTTPS](/docs/de/admin-guide/https.md)).
- CSRF-/XSS-Schutz, Rate-Limiting, Security-Header (CSP, HSTS).

## System & FFmpeg

- **Keine Shell-Ausführung**: FFmpeg/ffprobe/mount werden mit Argumentlisten gestartet.
- **Path-Traversal-Schutz**: alle Pfade auf konfigurierte Wurzeln beschränkt.
- **Sichere Uploads**: Typ-/Größenprüfung, generierte Dateinamen.
- Mount-Credentials in restriktiven `0600`-Dateien.

## Audit-Log

CastCore protokolliert sicherheitsrelevante Aktionen im **Audit-Log** (UI: `/audit`,
nur Admin). Erfasst werden u. a.: **Login**, **Stream Start/Stop/Restart**,
**Backup erstellen/wiederherstellen**, **Benutzer anlegen/löschen** – jeweils mit
Akteur, Aktion, Ziel, IP und Zeitstempel.

> 🔐 Das Audit-Log ist von **Backup/Restore ausgenommen** – es überlebt eine
> Wiederherstellung und bleibt so nachvollziehbar.

## Checkliste

- [ ] `SECRET_KEY` und `ENCRYPTION_KEY` einzigartig gesetzt und gesichert
- [ ] HTTPS aktiv, gültiges Zertifikat
- [ ] Nur benötigte Ports veröffentlicht
- [ ] Backups eingerichtet und getestet ([Backup & Restore](/docs/de/user-guide/backup-restore.md))
- [ ] Rollen sparsam vergeben

## Verwandte Seiten

- [Secrets-Verwaltung](/docs/de/admin-guide/secrets.md)
- [Rollen](/docs/de/reference/roles.md)
- [Backup & Restore](/docs/de/user-guide/backup-restore.md)

---
_Stand: 2026-06-24 · Status: Stabil_

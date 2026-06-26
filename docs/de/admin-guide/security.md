---
title: "Security Best Practices"
description: "Härtung, Rollen, Secrets, sichere Uploads, Audit."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-26
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
- Optionale **Zwei-Faktor-Authentifizierung (2FA / TOTP)** pro Benutzer.

## Zwei-Faktor-Authentifizierung (2FA)

CastCore unterstützt zeitbasierte Einmalcodes (**TOTP**, RFC 6238), kompatibel mit
gängigen Authenticator-Apps (Google Authenticator, Aegis, 1Password, …).

**Einrichten** (jeder Benutzer für sein eigenes Konto, unter **Einstellungen → Profil**):

1. **2FA einrichten** wählen. CastCore erzeugt ein geheimes Schlüsselmaterial.
2. Den angezeigten `otpauth://`-Link bzw. den manuellen Schlüssel in der
   Authenticator-App hinterlegen.
3. Einen aktuellen 6-stelligen Code eingeben und **Aktivieren**. Erst dann ist 2FA aktiv.

**Anmeldung:** Ist 2FA aktiv, fragt CastCore nach Benutzername und Passwort zusätzlich
den aktuellen Code ab.

**Deaktivieren:** Unter **Einstellungen → Profil** durch Eingabe eines gültigen Codes –
das verhindert versehentliches Abschalten durch Dritte.

> 🔐 Das TOTP-Geheimnis wird wie alle Secrets **verschlüsselt at-rest** gespeichert
> (Fernet, `ENCRYPTION_KEY`) und nie im Klartext zurückgegeben.
>
> ⚠️ Geht der zweite Faktor verloren, kann ein **Admin** 2FA für den betroffenen
> Benutzer zurücksetzen: **Benutzerverwaltung** (`/users`) → Zeile des Benutzers →
> **2FA zurücksetzen**. Danach meldet sich der Benutzer wieder nur mit Passwort an und
> kann 2FA bei Bedarf neu einrichten. Bewahre zusätzlich Backup-Codes deiner App sicher auf.

Siehe auch: [Einstellungen](/docs/de/user-guide/settings.md).

## Secrets

- Verschlüsselung at-rest mit **Fernet** (`ENCRYPTION_KEY` aus der Umgebung):
  Stream-Keys, Plattform-Tokens, OAuth-Refresh-Tokens, SMB-Passwörter,
  Benachrichtigungs-Secrets.
- Secrets sind **write-only** über die API und werden **maskiert** zurückgegeben.
- **Nie im Log.** Command-Vorschauen maskieren Stream-Keys in URLs.
- Details: [Secrets-Verwaltung](/docs/de/admin-guide/secrets.md).

## Transport & Web

- HTTPS über den Reverse Proxy ([HTTPS](/docs/de/admin-guide/https.md)).
- Security-Header am Reverse Proxy: **HSTS**, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy` (Caddy/nginx). Ein **CSP**-Header ist derzeit **nicht** gesetzt.
- Die API ist **Bearer-Token-basiert** (kein Cookie-Login) – klassische Cookie-CSRF-Angriffe
  greifen daher nicht; einen dedizierten CSRF-Token gibt es bewusst nicht.

## Rate-Limiting

Sicherheitskritische Auth-Endpunkte sind **gedrosselt** (Redis-basiert, festes Zeitfenster):
`POST /auth/login`, `/auth/refresh`, `/auth/2fa/verify`, `/tokens` (Erstellung) und
`/setup/admin`. Pro Client-IP sind standardmäßig **10 Versuche je 300 s** erlaubt; danach
antwortet die API mit `429` und dem übersetzbaren Code `auth.rate_limited` (inkl.
`Retry-After`-Header).

- Konfigurierbar über `RATE_LIMIT_ENABLED`, `RATE_LIMIT_AUTH_ATTEMPTS`,
  `RATE_LIMIT_AUTH_WINDOW_SECONDS` ([Umgebungsvariablen](/docs/de/reference/environment-variables.md)).
- Die Client-IP wird aus dem ersten `X-Forwarded-For`-Eintrag bestimmt – ein korrekt
  konfigurierter Reverse Proxy ist daher Voraussetzung.
- **Fail-open:** Ist Redis nicht erreichbar, wird **nicht** blockiert (kein versehentliches
  Aussperren). Für zusätzliche Härtung kann der Reverse Proxy ebenfalls drosseln (Caddy
  `rate_limit` bzw. nginx `limit_req`).

## System & FFmpeg

- **Keine Shell-Ausführung**: FFmpeg/ffprobe/mount werden mit Argumentlisten gestartet.
- **Path-Traversal-Schutz**: alle Pfade auf konfigurierte Wurzeln beschränkt.
- **Sichere Uploads**: Typ-/Größenprüfung, generierte Dateinamen.
- Mount-Credentials in restriktiven `0600`-Dateien.
- **Minimales Prozess-Environment**: gespawnte FFmpeg-Prozesse erhalten **keine** CastCore-
  Secrets (SECRET_KEY/ENCRYPTION_KEY/DB-Zugang) in ihrer Umgebung.
- **Container-Härtung**: `no-new-privileges` für alle App-Dienste; der Worker (verarbeitet
  potenziell untrusted Medien) zusätzlich `cap_drop: ALL` und als **Nicht-Root**.

## FFmpeg-Decoder-Sicherheit (CVE-2026-8461 / MagicYUV)

FFmpeg dekodiert fremde Mediendaten – die Version ist daher sicherheitsrelevant. CastCore
erkennt die installierte FFmpeg/ffprobe-Version, **warnt bei Versionen < 8.1.2** und behandelt
riskante Codecs (z. B. MagicYUV) gesondert (Safe-Media-Modus, Preflight-Block, Medien-Badge).
Details und Patch-Wege: [FFmpeg-Anforderungen & Sicherheit](/docs/de/admin-guide/ffmpeg-requirements.md).

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
_Stand: 2026-06-26 · Status: Stabil_

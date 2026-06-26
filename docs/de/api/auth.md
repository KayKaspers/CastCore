---
title: "API: Auth"
description: "Login, JWT-Refresh, Logout, API-Tokens."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-25
---

# API: Auth

> Authentifizierung über JWT (Access + rotierender Refresh).

**Zielgruppe:** Entwickler / Integratoren.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Anmeldung → `access_token`, `refresh_token`, `user` (optional `totp_code`) |
| `POST` | `/api/v1/auth/refresh` | Neues Token-Paar aus Refresh-Token |
| `POST` | `/api/v1/auth/logout` | Eigene Sessions widerrufen |
| `GET` | `/api/v1/auth/me` | Aktuelles Profil |
| `POST` | `/api/v1/auth/2fa/setup` | 2FA einrichten → `secret`, `otpauth_uri` |
| `POST` | `/api/v1/auth/2fa/verify` | 2FA aktivieren (Body `{ "code": "123456" }`) |
| `POST` | `/api/v1/auth/2fa/disable` | 2FA deaktivieren (gültiger Code nötig) |
| `GET` | `/api/v1/tokens` | Eigene API-Tokens auflisten |
| `POST` | `/api/v1/tokens` | API-Token erstellen → `token` (nur einmalig) |
| `DELETE` | `/api/v1/tokens/{id}` | API-Token widerrufen |

## Beispiel: Login

```bash
curl -k -X POST https://<host>/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"username":"admin","password":"<geheim>"}'
```

Antwort:
```json
{ "access_token": "…", "refresh_token": "…", "token_type": "bearer", "user": { … } }
```

Ist für das Konto **2FA** aktiv, antwortet `/login` ohne `totp_code` mit `401` und dem
Fehlercode `auth.totp_required`; bei falschem Code mit `auth.totp_invalid`. Wiederhole den
Login dann mit `"totp_code":"123456"`.

## Token-Nutzung

```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer <access_token>'
```

## Persönliche API-Tokens

Für nicht-interaktive Clients (Skripte, CI) erstellst du einen langlebigen
**persönlichen Zugriffstoken** – in der UI unter **Einstellungen → API-Tokens** oder per API:

```bash
curl -k -X POST https://<host>/api/v1/tokens \
  -H 'authorization: Bearer <access_token>' \
  -H 'content-type: application/json' \
  -d '{"name":"ci-bot","expires_in_days":90}'
```

Antwort (der Klartext-Token erscheint **nur dieses eine Mal**):
```json
{ "id": "…", "name": "ci-bot", "token": "cc_…", "expires_at": "…", "created_at": "…" }
```

Der Token wird dann wie ein Access-Token verwendet:
```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer cc_…'
```

- Tokens beginnen mit dem Präfix `cc_` und handeln mit den **Rechten ihres Besitzers**.
- Sie werden **nur als Hash** gespeichert; der Klartext ist nicht wiederherstellbar.
- `expires_in_days` ist optional (ohne Angabe laufen sie nicht ab). Widerrufen jederzeit per
  `DELETE /api/v1/tokens/{id}`.

## Hinweise

- Access-Token kurzlebig (`ACCESS_TOKEN_TTL_MINUTES`), Refresh rotiert und ist widerrufbar.
- Passwörter werden mit **argon2id** gehasht.
- Behandle API-Tokens wie Passwörter – nicht in Repos/Logs committen.

## Verwandte Seiten

- [Rollen](/docs/de/reference/roles.md) · [Security](/docs/de/admin-guide/security.md)

---
_Stand: 2026-06-25 · Status: Stabil_

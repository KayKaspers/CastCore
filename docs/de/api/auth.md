---
title: "API: Auth"
description: "Login, JWT-Refresh, Logout, API-Tokens."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-24
---

# API: Auth

> Authentifizierung über JWT (Access + rotierender Refresh).

**Zielgruppe:** Entwickler / Integratoren.

## Endpunkte

| Methode | Pfad | Zweck |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Anmeldung → `access_token`, `refresh_token`, `user` |
| `POST` | `/api/v1/auth/refresh` | Neues Token-Paar aus Refresh-Token |
| `POST` | `/api/v1/auth/logout` | Eigene Sessions widerrufen |
| `GET` | `/api/v1/auth/me` | Aktuelles Profil |

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

## Token-Nutzung

```bash
curl -k https://<host>/api/v1/auth/me -H 'authorization: Bearer <access_token>'
```

## Hinweise

- Access-Token kurzlebig (`ACCESS_TOKEN_TTL_MINUTES`), Refresh rotiert und ist widerrufbar.
- Passwörter werden mit **argon2id** gehasht.

## Verwandte Seiten

- [Rollen](/docs/de/reference/roles.md) · [Security](/docs/de/admin-guide/security.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Reverse Proxy"
description: "Caddy (Standard) oder Nginx vor CastCore betreiben."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Reverse Proxy

> CastCore wird hinter einem Reverse Proxy betrieben, der TLS terminiert und Anfragen auf
> Frontend bzw. Backend verteilt.

**Zielgruppe:** Administratoren.

## Routing-Prinzip

- `/api/*` → **backend** (inkl. WebSockets für Live-Logs/Status)
- alles andere → **frontend** (das gebaute SPA)

## Caddy (Standard)

Die mitgelieferte `deploy/caddy/Caddyfile` macht genau das und holt automatisch
Zertifikate (bei `localhost` ein lokal vertrauenswürdiges Self-Signed). `DOMAIN` und
`ACME_EMAIL` kommen aus der Umgebung.

```caddyfile
{$DOMAIN} {
  handle /api/* { reverse_proxy backend:8000 }
  handle       { reverse_proxy frontend:80 }
}
```

## Nginx (Alternative)

Für bestehende Nginx-Setups liegt `deploy/nginx/castcore.conf` bei: TLS-Terminierung +
WebSocket-Upgrade, `/api/` → `127.0.0.1:8000`, Rest → Frontend. Zertifikate separat
beschaffen (z. B. certbot).

## WebSockets

Live-Logs/Status laufen über `/api/v1/ws/...`. Der Proxy muss **Upgrade/Connection**-Header
durchreichen (Caddy macht das automatisch; im Nginx-Beispiel ist es konfiguriert).

## Hinweise

> ⚠️ Channel-HLS/EPG/M3U-Endpunkte sind im MVP öffentlich. Wenn sie nicht erreichbar sein
> sollen, am Reverse Proxy einschränken.

## Verwandte Seiten

- [HTTPS / TLS](/docs/de/admin-guide/https.md)
- [Reverse-Proxy-Probleme](/docs/de/troubleshooting/docker.md)

---
_Stand: 2026-06-24 · Status: Stabil_

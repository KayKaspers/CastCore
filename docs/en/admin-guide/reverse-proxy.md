---
title: "Reverse proxy"
description: "Run Caddy (default) or Nginx in front of CastCore."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Reverse proxy

> CastCore runs behind a reverse proxy that terminates TLS and routes requests to the
> frontend or backend.

**Audience:** administrators.

## Routing principle

- `/api/*` → **backend** (incl. WebSockets for live logs/status)
- everything else → **frontend** (the built SPA)

## Caddy (default)

The bundled `deploy/caddy/Caddyfile` does exactly this and obtains certificates
automatically (for `localhost`, a locally-trusted self-signed one). `DOMAIN` and
`ACME_EMAIL` come from the environment.

```caddyfile
{$DOMAIN} {
  handle /api/* { reverse_proxy backend:8000 }
  handle       { reverse_proxy frontend:80 }
}
```

## Nginx (alternative)

For existing Nginx setups there is `deploy/nginx/castcore.conf`: TLS termination +
WebSocket upgrade, `/api/` → `127.0.0.1:8000`, rest → frontend. Obtain certificates
separately (e.g. certbot).

## WebSockets

Live logs/status use `/api/v1/ws/...`. The proxy must forward the **Upgrade/Connection**
headers (Caddy does this automatically; the Nginx example is configured for it).

## Notes

> ⚠️ Channel HLS/EPG/M3U endpoints are public in the MVP. If they should not be reachable,
> restrict them at the reverse proxy.

## Related pages

- [HTTPS / TLS](/docs/en/admin-guide/https.md)
- [Reverse-proxy problems](/docs/en/troubleshooting/docker.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

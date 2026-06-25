---
title: "HTTPS / TLS"
description: "Automatic and manual certificates for CastCore."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# HTTPS / TLS

> HTTPS is provided by the reverse proxy. With Caddy it is nearly automatic.

**Audience:** administrators.

## Public domain (automatic)

1. Set `DOMAIN` in `.env` to the **public hostname** (DNS must point to the server).
2. Set `ACME_EMAIL`.
3. Start the stack – Caddy obtains a Let's Encrypt certificate automatically.

Requirement: ports **80** and **443** are reachable from outside.

## localhost (development)

With `DOMAIN=localhost`, Caddy issues a **locally-trusted** self-signed certificate. The
browser may show a warning you accept.

## Manual certificates (Nginx)

When using Nginx (`deploy/nginx/castcore.conf`), obtain certificates separately (e.g.
certbot) and point `ssl_certificate`/`ssl_certificate_key` at them.

## Notes

> 🔐 Always enable HTTPS in production. Security headers (HSTS, CSP) are already set in the
> Caddy/Nginx config.

## If something fails

- Certificate not issued → check DNS, ports 80/443, `ACME_EMAIL`.
- See [Docker problems](/docs/en/troubleshooting/docker.md).

## Related pages

- [Reverse proxy](/docs/en/admin-guide/reverse-proxy.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

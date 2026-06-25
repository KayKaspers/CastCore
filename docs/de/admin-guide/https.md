---
title: "HTTPS / TLS"
description: "Automatische und manuelle Zertifikate für CastCore."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# HTTPS / TLS

> HTTPS wird über den Reverse Proxy bereitgestellt. Mit Caddy ist es nahezu automatisch.

**Zielgruppe:** Administratoren.

## Öffentliche Domain (automatisch)

1. `DOMAIN` in der `.env` auf den **öffentlichen Hostnamen** setzen (DNS muss auf den
   Server zeigen).
2. `ACME_EMAIL` setzen.
3. Stack starten – Caddy holt automatisch ein Let's-Encrypt-Zertifikat.

Voraussetzung: Ports **80** und **443** sind von außen erreichbar.

## localhost (Entwicklung)

Bei `DOMAIN=localhost` stellt Caddy ein **lokal vertrauenswürdiges** Self-Signed-Zertifikat
aus. Im Browser erscheint ggf. eine Warnung, die du akzeptierst.

## Manuelle Zertifikate (Nginx)

Bei Nutzung von Nginx (`deploy/nginx/castcore.conf`) Zertifikate separat beschaffen
(z. B. certbot) und auf `ssl_certificate`/`ssl_certificate_key` verweisen.

## Hinweise

> 🔐 Aktiviere immer HTTPS im Produktivbetrieb. Security-Header (HSTS, CSP) sind in der
> Caddy-/Nginx-Konfiguration bereits gesetzt.

## Bei Problemen

- Zertifikat wird nicht ausgestellt → DNS, Ports 80/443, `ACME_EMAIL` prüfen.
- Siehe [Docker-Probleme](/docs/de/troubleshooting/docker.md).

## Verwandte Seiten

- [Reverse Proxy](/docs/de/admin-guide/reverse-proxy.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-24 · Status: Stabil_

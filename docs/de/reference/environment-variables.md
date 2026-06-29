---
title: "Umgebungsvariablen"
description: "Referenz aller `.env`-Variablen."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-26
---

# Umgebungsvariablen

> Konfiguration erfolgt über die Datei `.env` (Vorlage: `.env.example`).

**Zielgruppe:** Administratoren. Siehe auch [Konfiguration](/docs/de/reference/configuration.md).

## Allgemein

| Variable | Beschreibung | Beispiel |
| --- | --- | --- |
| `CASTCORE_ENV` | `production` oder `development` | `production` |
| `DOMAIN` | öffentlicher Hostname (Reverse Proxy) | `castcore.example.com` |
| `TZ` | Zeitzone | `Europe/Berlin` |
| `DEFAULT_LANGUAGE` | Standardsprache `de`/`en` | `de` |

## Sicherheit (unbedingt ändern)

| Variable | Beschreibung |
| --- | --- |
| `SECRET_KEY` | Signierschlüssel für JWT (64 Hex-Zeichen) |
| `ENCRYPTION_KEY` | Fernet-Key für verschlüsselte Secrets – **sicher aufbewahren** |
| `ACCESS_TOKEN_TTL_MINUTES` | Gültigkeit Access-Token (Default 30) |
| `REFRESH_TOKEN_TTL_DAYS` | Gültigkeit Refresh-Token (Default 14) |

## Datenbank & Redis

| Variable | Beschreibung |
| --- | --- |
| `POSTGRES_HOST` / `_PORT` / `_DB` / `_USER` / `_PASSWORD` | PostgreSQL-Verbindung |
| `REDIS_HOST` / `_PORT` / `_PASSWORD` | Redis-Verbindung |

## Pfade

| Variable | Default |
| --- | --- |
| `DATA_DIR` | `/data` |
| `MEDIA_DIR` | `/data/media` |
| `RECORDINGS_DIR` | `/data/recordings` |
| `LOG_DIR` | `/data/logs` |
| `BACKUP_DIR` | `/data/backups` |
| `MOUNT_DIR` | `/data/mounts` |
| `THUMBNAIL_DIR` | `/data/thumbnails` |

## FFmpeg & Proxy

| Variable | Beschreibung |
| --- | --- |
| `FFMPEG_PATH` / `FFPROBE_PATH` | Pfade zu FFmpeg/ffprobe |
| `SAFE_MEDIA_PROCESSING_ENABLED` | Safe-Media-Modus für untrusted Quellen (Standard `true`) |
| `MEDIA_AUTOTHUMBNAILS_ENABLED` | automatische Thumbnail-Erzeugung (Standard `true`) |
| `BLOCK_RISKY_CODECS` | riskante Codecs im Preflight blockieren (Standard `true`) |
| `RISKY_CODECS_BLOCKLIST` | zusätzliche riskante Codecs, kommagetrennt (Standard `magicyuv`) |
| `ACME_EMAIL` | E-Mail für automatische HTTPS-Zertifikate (Caddy) |
| `CSP_ENABLED` | Content-Security-Policy-Header von Caddy senden an/aus (Standard `true`) |
| `CSP_REPORT_ONLY` | `true` = Report-Only (Standard, nichts wird blockiert), `false` = erzwungen |
| `RATE_LIMIT_ENABLED` | Auth-Rate-Limiting an/aus (Standard `true`) |
| `RATE_LIMIT_AUTH_ATTEMPTS` | erlaubte Versuche je Fenster und Client-IP (Standard `10`) |
| `RATE_LIMIT_AUTH_WINDOW_SECONDS` | Länge des Zeitfensters in Sekunden (Standard `300`) |
| `MEDIAMTX_ENABLED` / `MEDIAMTX_API_URL` / `MEDIAMTX_RTSP_URL` | optionale MediaMTX-Integration (Aktivierung, API-Adresse, RTSP-Pull-Basis) |
| `PUBLIC_BASE_URL` | öffentliche URL der Instanz (für OAuth-Redirects); z. B. `https://stream.example.com` |
| `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` | YouTube-OAuth (leer = deaktiviert) |
| `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` | Twitch-OAuth (leer = deaktiviert) |

## Hinweise

> 🔐 Niemals echte Werte committen – die `.env` ist git-ignoriert. Secrets generieren:
> `openssl rand -hex 32` (SECRET_KEY), `openssl rand -base64 32 | tr '+/' '-_'` (Fernet).

## Verwandte Seiten

- [Secrets-Verwaltung](/docs/de/admin-guide/secrets.md)
- [Konfiguration](/docs/de/reference/configuration.md)

---
_Stand: 2026-06-26 · Status: Stabil_

---
title: "Umgebungsvariablen"
description: "Referenz aller `.env`-Variablen."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
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
| `ACME_EMAIL` | E-Mail für automatische HTTPS-Zertifikate (Caddy) |
| `MEDIAMTX_ENABLED` / `MEDIAMTX_API_URL` / `MEDIAMTX_RTSP_URL` | optionale MediaMTX-Integration (Aktivierung, API-Adresse, RTSP-Pull-Basis) |

## Hinweise

> 🔐 Niemals echte Werte committen – die `.env` ist git-ignoriert. Secrets generieren:
> `openssl rand -hex 32` (SECRET_KEY), `openssl rand -base64 32 | tr '+/' '-_'` (Fernet).

## Verwandte Seiten

- [Secrets-Verwaltung](/docs/de/admin-guide/secrets.md)
- [Konfiguration](/docs/de/reference/configuration.md)

---
_Stand: 2026-06-24 · Status: Stabil_

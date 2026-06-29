# Architektur

> Maßgeblich ist [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) und die `README.md`.
> Diese Datei ist die Kurzfassung für den Nova-Workflow.

## Technologiestack

| Schicht | Wahl |
| --- | --- |
| Backend / API | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Pydantic v2 · Alembic |
| Process Manager | Dedizierter asyncio-Supervisor für langlaufende FFmpeg-Prozesse |
| Worker | arq (Redis) für Scans, ffprobe, Thumbnails, Backups |
| Datenbank | PostgreSQL 16 |
| Cache / Queue / PubSub | Redis 7 |
| Frontend | React 18 · TypeScript · Vite · Tailwind · i18next · zustand |
| Reverse Proxy | Caddy (automatisches HTTPS) |
| Optionaler Router | MediaMTX (RTSP/RTMP/SRT/WebRTC/HLS) |

## Grundstruktur

- `backend/` — FastAPI-App (`app/`: api, services, models, core, schemas), Alembic-Migrationen, Tests
- `process_manager/` — eigener Supervisor, der FFmpeg-Stream-Prozesse spawnt/überwacht
- `worker/` — arq-Worker für kurze Async-Jobs
- `frontend/` — React/Vite SPA (Brand-Tokens, i18n DE/EN)
- `docs/` — bilinguale Doku (`de/`, `en/`) + Architektur/API/Data-Model, in-App-Viewer unter `/docs`
- `deploy/` — Caddy/Prometheus/MediaMTX-Configs
- `branding/` — Corporate Design (Logos, Favicons, SVGs)
- `scripts/` — `check_docs.py`, `install.sh`, `update.sh`, `uninstall.sh`
- `shared/` — geteilte Definitionen

## Wichtige Module

- **Auth & RBAC** — JWT + rotierende Refresh-Tokens, Rollen Admin/Operator/Viewer, 2FA (TOTP), API-Tokens, Rate-Limiting
- **Stream-Jobs** — shell-freier FFmpeg-Command-Builder, Multi-Output, Live-Logs (WebSocket/Redis), Auto-Restart/Self-Healing
- **Process Manager** — Prozesssteuerung getrennt vom Worker (zentrale Architekturentscheidung)
- **Preflight 2.0** — persistierte Startklar-Reports + optionales Start-Gate
- **Health & Diagnostics** — Health-Score + Diagnose-Assistent (verständliche Fehlererklärungen)
- **Monitoring** — psutil-Metriken + Prometheus-Exporter
- **Storage** — lokal + SMB/CIFS; Medienbibliothek, Playlists
- **Channels** — lineare Kanäle (HLS/EPG/M3U), Recording, Scheduler, Notifications, Backup/Restore
- **Plattformen** — OAuth (YouTube/Twitch), Metadaten-Push, Readiness-Check
- **Safe-Media-Mode** — FFmpeg-Versionserkennung + CVE-2026-8461-Mitigation

## Architekturregeln

- Modular entwickeln, keine unnötigen Komplettumbauten
- Keine neuen Frameworks ohne Begründung/Freigabe
- Docker-first · Security-first · Documentation-first
- Keine Feature-Änderung ohne DE+EN-Doku-Update (bindende Regel)

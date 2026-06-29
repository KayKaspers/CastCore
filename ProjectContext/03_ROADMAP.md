# Roadmap

> Maßgeblich ist [`docs/ROADMAP.md`](../docs/ROADMAP.md). Kurzfassung mit Ist-Stand:

## Phase 1 – Foundation ✅

- [x] Grundstruktur / Scaffold
- [x] Docker-Stack (compose, alle Services)
- [x] README + Security-Doku
- [x] Setup Wizard + Systemcheck
- [x] Bilinguale Dokumentation (DE/EN, in-App-Viewer)
- [x] Auth/Setup, RBAC, 2FA, API-Tokens

## Phase 2 – Core Features ✅ (weitgehend)

- [x] Stream-Jobs, FFmpeg-Command-Builder, Multi-Output
- [x] Process Manager + Status-Consumer + Self-Healing
- [x] Profile/Destinations, Live-Logs, Dry-Run/Teststream
- [x] **Preflight / Systemcheck (jetzt Preflight 2.0: persistiert + Start-Gate)**
- [x] Monitoring + Prometheus, Health-Score + Diagnose-Assistent
- [x] Medienbibliothek, Playlists, Recording/Replay, Scheduler, Notifications, Backup/Restore
- [ ] Simple/Expert Mode (UI-Umschaltung) — offen/teilweise

## Phase 3 – Beta

- [x] Lineare Kanäle (HLS/EPG/M3U), Fallback, interner hls.js-Player
- [x] Plattform-OAuth (YouTube/Twitch), Metadaten-Push, Readiness-Check
- [x] CI (Backend/Frontend/Docs/Compose), Audit-Log
- [x] FFmpeg ≥ 8.1.2 als verifizierte Standard-Binary (copy-Variante, Build-Gate, Digest-Pin)
- [ ] OAuth-Push gegen echte Plattform-APIs verifizieren
- [ ] Security-Review / Hardening (CSP, Backend/PM non-root)
- [ ] Frontend-Tests, Migrationstests, automatisierte E2E
- [ ] Release-Doku, Support-Konzept finalisieren

## Phase 4 – Erweiterung (begonnen)

- [x] Prometheus-Exporter
- [ ] Weitere Storage-Backends (NFS/SFTP/WebDAV/rclone/Cloud)
- [ ] Jellyfin/Plex-Vorbereitung
- [ ] Geplante Channel-Programme / Rotation

# Offene Aufgaben

> Abgeleitet aus `README.md` („Known gaps“) und dem aktuellen Stand (2026-06-29).

## Hoch

- [ ] `main` (inkl. Preflight-2.0-Commit `d7e306a`) nach GitHub pushen — auf Freigabe
- [ ] FFmpeg ≥ 8.1.2 als **verifizierte** Standard-Binary in den Images (aktuell Debian-Build + Static-Build-Pfad + Runtime-Warnung)
- [ ] Security-Hardening: CSP-Header; Backend/Process-Manager non-root (Worker ist bereits non-root + cap_drop)

## Mittel

- [ ] OAuth-Metadaten-Push gegen echte YouTube/Twitch-APIs verifizieren (bisher nur mit Mocks getestet)
- [ ] Simple/Expert-Mode-Umschaltung im Frontend
- [ ] Frontend-Tests + Migrationstests; E2E von manuell (`workflow_dispatch`) auf automatisiert
- [ ] `install.sh` / `update.sh` / `uninstall.sh` vollständig verifizieren

## Niedrig

- [ ] Weitere Storage-Backends (NFS/SFTP/WebDAV/rclone/Cloud)
- [ ] Geplante Channel-Programme / Rotation / Auto-Rescan
- [ ] Jellyfin/Plex-Vorbereitung
- [ ] Frontend-Bundle splitten (Vite-Warnung: Chunk > 500 kB)
- [ ] Vorbestehende ESLint-Warnungen in `MetadataPanel.tsx` und `DocsPage.tsx` bereinigen

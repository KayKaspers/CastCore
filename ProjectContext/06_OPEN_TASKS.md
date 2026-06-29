# Offene Aufgaben

> Abgeleitet aus `README.md` („Known gaps“) und dem aktuellen Stand (2026-06-29).

## Hoch

- [ ] **GPU-Encoding (NVENC/QSV/VAAPI)**: Capability-Detection, NVIDIA Container Toolkit,
      VAAPI `/dev/dri`, Encoder-Auswahl Simple/Expert, end-to-end verifizieren
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

## Erledigt (jüngst)

- [x] CI-Smoke-Job `docker-ffmpeg-smoke` (baut copy-Variante, prüft ffmpeg/ffprobe ≥ 8.1.2 + Negativtest) — 2026-06-29
- [x] FFmpeg ≥ 8.1.2 verifizierte Standard-Binary (copy-Variante, Build-Gate, Digest/SHA-Pin) — 2026-06-29
- [x] Preflight 2.0 + ProjectContext + CI-Regeln gepusht, CI grün — 2026-06-29
- [x] Tech-Debt `generated`-Feld aus `docs-status.json` entfernt — 2026-06-29

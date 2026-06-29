# Aktueller Projektstatus

> Stand: 2026-06-29 · maßgeblich ist `CHANGELOG.md`. Claude liest diese Datei vor jeder Arbeit.

## Aktueller Stand

🟡 **Early Beta / fortgeschrittenes Alpha.** Kern gebaut und lauffähig auf Docker; für
self-hosted Früheinsatz geeignet, **noch nicht production-hardened**. 66 Commits, Migrations-Head **0016**.

Funktional u. a.: Auth (JWT+Refresh, RBAC, 2FA, API-Tokens, Rate-Limiting), Stream-Jobs
mit shell-freiem Command-Builder + Multi-Output, Live-Logs, Auto-Restart, Monitoring +
Prometheus, Health-Score + Diagnose-Assistent, **Preflight 2.0** (persistierte Reports +
Start-Gate), Safe-Media-Mode (CVE-2026-8461), lokal+SMB-Storage, Medienbibliothek,
Playlists, Channels (HLS/EPG/M3U), Recording, Scheduler, Notifications, Backup/Restore,
MediaMTX-Ingest, Plattform-OAuth (YouTube/Twitch) mit Metadaten-Push + Readiness-Check,
vollständige bilinguale Doku, CI (Backend ruff/mypy/pytest, Frontend, Docs, Compose).

## Letzter abgeschlossener Schritt

**CI-Smoke-Job `docker-ffmpeg-smoke`**: baut Backend/PM/Worker mit `FFMPEG_VARIANT=copy` und
prüft ffmpeg/ffprobe ≥ 8.1.2 je Image (+ Negativtest am Build-Gate). Reguläre CI-Tests bleiben
ffmpeg-frei. (Davor: FFmpeg ≥ 8.1.2 Build-Pfad mit Default `copy` + Build-Gate + Digest-Pin;
Preflight 2.0 — alle gepusht, CI grün.)

## Aktuelle Priorität

1. GPU-Encoding (NVENC/QSV/VAAPI) als separater Folge-Task inkl. Capability-Detection.
2. Security-Hardening (CSP, Backend/PM non-root).
3. OAuth-Push gegen echte Plattform-APIs verifizieren.

## Bekannte Probleme

- `.env` ist gitignored und ging beim Repo-Umzug verloren → am 2026-06-29 neu generiert.
- `castcore_pg`-Volume hatte altes Passwort → non-destruktiv via `ALTER USER` korrigiert.
- GPU-Encoding noch nicht end-to-end verifiziert (Treiber + GPU-Container-Runtime nötig).
- Weitere Produkt-Lücken siehe `README.md` → „Known gaps“.

## Wichtiger Hinweis für Claude

Claude soll diese Datei vor jeder Arbeit lesen und nach jedem Schritt aktualisieren.

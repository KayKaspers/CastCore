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

**Preflight 2.0** — persistierte Startklar-Reports + optionales Start-Gate.
Commit `d7e306a` auf `main` (lokal committet, **noch nicht gepusht**).
Verifiziert: pytest (122), ruff, mypy, Frontend tsc+build, check_docs, `docker compose config`.

## Aktuelle Priorität

1. Optional: `main` nach GitHub pushen (auf Freigabe von Nova/Cursor-Review).
2. ProjectContext-Pflege abschließen und mit `CLAUDE.md`/`README`/`docs` synchron halten.
3. Bekannte Lücken (s. `06_OPEN_TASKS.md`) priorisieren — v. a. FFmpeg ≥ 8.1.2 als verifizierte Standard-Binary.

## Bekannte Probleme

- Preflight-2.0-Commit ist lokal, **nicht gepusht** (Divergenzrisiko zu GitHub).
- `.env` ist gitignored und ging beim Repo-Umzug verloren → am 2026-06-29 neu generiert.
- `castcore_pg`-Volume hatte altes Passwort → non-destruktiv via `ALTER USER` korrigiert.
- Weitere Produkt-Lücken siehe `README.md` → „Known gaps“.

## Wichtiger Hinweis für Claude

Claude soll diese Datei vor jeder Arbeit lesen und nach jedem Schritt aktualisieren.

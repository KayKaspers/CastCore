# Changelog

> Maßgeblich und chronologisch: `CHANGELOG.md` im Repo-Root. Hier nur Nova-relevante Schritte.

## Unreleased

- **2026-06-29 — CI-Smoke-Job `docker-ffmpeg-smoke`**: baut Backend/PM/Worker mit
  `FFMPEG_VARIANT=copy`, prüft ffmpeg/ffprobe ≥ 8.1.2 je Image + Negativtest (alte Quelle muss
  am Gate scheitern). Reguläre CI-Tests bleiben ffmpeg-frei.
- **2026-06-29 — FFmpeg ≥ 8.1.2 verifizierter Build-Pfad** (CVE-2026-8461): Docker-Default
  `FFMPEG_VARIANT=copy` (Multi-Stage-COPY aus `mwader/static-ffmpeg:8.1.2`, Tag+Digest gepinnt),
  Build-Gate (≥ 8.1.2 sonst Abbruch), `static` mit SHA256, `apt` als Fallback; install.sh
  Strict-Modus; DE/EN-Doku + README aktualisiert; `generated`-Feld aus docs-status.json entfernt.
- **2026-06-29 — Preflight 2.0** (Commit `d7e306a`, gepusht, CI grün):
  persistierte Startklar-Reports (Migration 0016), strukturierte code-basierte Checks,
  optionales Start-Gate (`PREFLIGHT_REQUIRED_BEFORE_START` / `PREFLIGHT_BLOCK_ON_RED` /
  `PREFLIGHT_REPORT_TTL_SECONDS`), neue Endpoints `/preflight/latest|reports|reports/{id}`,
  `start?override=true` (Admin, auditiert), Fehler-Codes `preflight.required|blocked`,
  diagnostics/monitoring lesen persistierte Reports. Frontend + DE/EN-i18n + Doku aktualisiert.
  Verifiziert: pytest (122), ruff, mypy, Frontend tsc+build, check_docs, compose config.
- **2026-06-29** — Repo nach `D:\Projects\CastCore` umgezogen; uncommittete Preflight-Arbeit
  verlustfrei übernommen; `.env` neu generiert; ProjectContext aus realem Stand befüllt.
- Projektkontext nach Nova Development Kit vorbereitet.

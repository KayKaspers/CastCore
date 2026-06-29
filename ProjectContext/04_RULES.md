# Projektregeln

> Maßgeblich ist `CLAUDE.md`. Diese Datei spiegelt die Regeln für den Nova-Workflow.

## Standardregeln

- Docker-first
- Documentation-first (keine Feature-Änderung ohne **DE+EN**-Doku-Update — bindend)
- Security-first
- Deutsch und Englisch
- Anfängerfreundlich
- Modular
- Simple Mode und Expert Mode
- README aktuell halten
- `.env.example` aktuell halten
- Keine Hardcoded Secrets

## Doku-Regel (bindend)

Bei jeder Code-/UI-/API-/Model-/Deploy-/Config-/Security-Änderung:
DE **und** EN-Seiten aktualisieren, `docs/docs-manifest.json` pflegen und
`scripts/check_docs.py` ausführen (regeneriert `docs-status.json` + `nav.json`, 0 Fehler).
CI: `.github/workflows/ci.yml` (Job „docs“).

## Support-Regeln

- Gemeinsamer Ko-fi-/Support-Link erlaubt (README, Footer, About, Doku)
- Nur dezent platzieren
- Keine Pop-ups
- Keine Paywall
- Keine aggressiven Spendenhinweise
- Keine gesperrten Funktionen für Nichtspender

## Arbeitsweise

- Nova plant. Claude implementiert. Cursor prüft. GitHub speichert. Nextcloud ist nur Ablage.
- Claude setzt immer nur den von Nova definierten nächsten Schritt um.
- Keine großen Architekturänderungen ohne Freigabe.
- Keine neuen Frameworks ohne Begründung.
- Nach jedem Schritt: Rückmeldung an Nova (siehe `CLAUDE.md`, „Pflicht nach jedem Schritt“).

## Verifikation auf Windows (kein Host-Python/Node)

Checks laufen in Containern:
- Backend: `docker compose up -d postgres` + `docker compose run --rm --no-deps -v "<repo>/backend:/app" backend sh -c "pip install -q -e '.[dev]' && pytest -q && ruff check app && mypy"`
- Docs: throwaway `python:3.12-slim` → `python scripts/check_docs.py`
- Frontend: `node:20` → `npm ci && npm run lint && npm run build`

## Test- & CI-Regeln (CI-taugliche Medien-Tests)

1. Backend-Unit- und Integrationstests in der GitHub-CI dürfen **kein echtes
   `ffmpeg`/`ffprobe`-Binary voraussetzen** — der CI-Backend-Job läuft auf einem
   ubuntu-Runner mit `setup-python` und installiert kein ffmpeg.
2. FFmpeg-/ffprobe-Aufrufe müssen in normalen Backend-Tests **gemockt** werden
   (z. B. `monkeypatch.setattr(preflight_service, "_ffprobe", ...)`,
   `monkeypatch.setattr(ffmpeg_inspect, "get_info", ...)`).
3. **Reale FFmpeg-Läufe** gehören nur in explizite Docker-/E2E-Tests oder
   manuell gestartete E2E-Workflows (`workflow_dispatch`), nicht in die Standard-CI.
4. Preflight-/Stream-/Capability-Tests müssen CI-tauglich bleiben und dürfen nicht
   davon abhängen, dass ffmpeg im GitHub-Backend-Job vorhanden ist.
5. **`docs-status.json` darf keine volatilen `generated`-Daten enthalten**, die an
   einem anderen Kalendertag als der CI-Lauf den Docs-Job brechen. Aktuell enthält
   die Datei noch ein `generated: <Datum>`-Feld → **Tech-Debt-TODO**: Feld aus der
   committeten Datei entfernen oder im CI-`git diff` ausschließen (siehe
   `06_OPEN_TASKS.md`).

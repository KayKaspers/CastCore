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

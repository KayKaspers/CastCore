---
title: "Tests, Linting, Typprüfung"
description: "pytest, ruff, mypy, tsc – lokal und in CI."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-26
---

# Tests, Linting, Typprüfung

> Qualitätssicherung für Backend, Frontend und Doku.

**Zielgruppe:** Entwickler.

## CI-Pipeline

Die GitHub-Actions-CI (`.github/workflows/ci.yml`) läuft bei jedem Push und Pull Request und
muss vor dem Merge grün sein. Sie besteht aus vier Jobs:

| Job | Prüfungen |
| --- | --- |
| **backend** | `ruff check app` · `mypy` · `pytest -q` |
| **frontend** | `npm ci` · `npm run lint` (ESLint) · `npm run build` (`tsc` + Vite) |
| **docs** | `python scripts/check_docs.py` (Struktur, DE/EN-Parität, Manifest, interne Links) |
| **compose** | `docker compose config` (Validierung von `docker-compose.yml`) |

## Backend-Tests (pytest)

Unit-Tests (z. B. Command Builder, Security, stream_service, Rate-Limiting) brauchen keine
DB/Redis:

```bash
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && ruff check app && mypy && pytest -q"
```
Oder mit lokalem Python 3.12: `cd backend && python -m pip install -e ".[dev]" && pytest`.

## API-Integrationstests

`tests/test_api_*.py` testen die HTTP-Schicht in-process über httpx **`ASGITransport`** (kein
Netzwerk; die App-Lifespan – also die Redis-Loops – wird bewusst **nicht** gestartet).

**DB-Strategie:** eine eigene PostgreSQL-Test-Datenbank **`castcore_test`**, isoliert von der
App-/Dev-DB:

- Schema wird einmalig pro Session via `Base.metadata.create_all` erzeugt.
- Vor jedem Test werden alle Tabellen geleert und die Standardrollen
  (`admin`/`operator`/`viewer`) neu eingespielt.
- Die App-Dependency `get_db` wird auf die Test-DB umgebogen.
- Verbindung über die `POSTGRES_*`-Variablen; DB-Name = `TEST_DB_NAME` (Standard
  `castcore_test`). Rate-Limiting ist in Tests deaktiviert.

**Externe Dienste** werden gemockt (z. B. die OAuth-Provider-Grenze
`oauth_service._post_token` / `fetch_account_name`). Es sind **keine** echten
Plattformzugänge nötig.

Abgedeckt sind u. a.: Setup-Status, Login/Refresh/Logout, 2FA-Flow, API-Tokens, RBAC
(Admin/Operator/Viewer), Protected Routes, Stream-Job-CRUD, Command-Preview (inkl.
Stream-Key-Maskierung), Preflight, OAuth-Account-Status und der Monitoring-Health-Endpoint.

Lokal in CI-Parität (Container erreicht den Compose-Postgres):

```bash
docker compose exec backend sh -c "pip install -q '.[dev]' && cd /app && pytest -q"
```

## End-to-End-Stream-Test (voller Stack)

`backend/e2e_stream.py` testet den **kompletten Stream-Lebenszyklus** über den echten Stack
(Backend + Redis + Process Manager + Status-Consumer): Job anlegen → **Command-Preview** →
**Start** → **Prozessstatus** (`running`) → **Logs empfangen** (Redis-Log-Kanal) →
**Output prüfen** (lokale Datei wächst) → **Stop** → **Endstatus** (`stopped`).

Es nutzt ausschließlich **sichere, lokale** Quellen/Outputs (lavfi `testsrc`, H.264, kein
Audio, MPEG-TS in eine Datei) – **keine externen Dienste, keine riskanten Codecs**. Eine
FFmpeg-Version < 8.1.2 (CVE-2026-8461) lässt den Test **nicht** scheitern, da nur die
Versions-*Warnung* betroffen ist und kein riskanter Codec verwendet wird.

```bash
docker compose up -d --build           # Stack starten (Skript liegt im Backend-Image)
docker compose exec backend python /app/e2e_stream.py
```

Das Skript legt einen Wegwerf-Admin in der laufenden DB an, fährt den Lebenszyklus über die
HTTP-API und räumt anschließend alles auf (Job, Ziel, Profil, Benutzer, Datei). In CI gibt es
dafür den separaten Workflow **`.github/workflows/e2e.yml`** (manuell über *Actions →
e2e → Run workflow*; bewusst nicht im PR-`ci`-Workflow, da er den ganzen Stack baut).

## Linting & Typen

- Backend: **ruff** (Lint) und **mypy** (Typen, Konfiguration in `pyproject.toml`).
- Frontend: **ESLint** (Flat-Config in `eslint.config.js`) plus **`tsc`** im `npm run build`.
  Reine Typprüfung: `npm run typecheck`.

## Doku-Check

```bash
python scripts/check_docs.py        # Struktur, DE/EN-Parität, Manifest, leere Seiten, Links
```
Erzeugt `docs-status.json` + `nav.json`; ist Teil der CI (Job **docs** in `ci.yml`).

## Noch nicht abgedeckt

Ehrliche Lücken (Stand der Testbasis):

- **Keine Frontend-Tests** (nur ESLint + `tsc`/Vite-Build).
- **Keine Migrationstests** – Integrationstests bauen das Schema via `create_all`, prüfen also
  nicht die Alembic-Migrationskette.
- Der **E2E-Stream-Test ist manuell** (`workflow_dispatch`), nicht Teil des PR-Gates.

## Lokaler Stack

Siehe [Lokales Testen](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).

## Verwandte Seiten

- [Mitwirken](/docs/de/developer-guide/contributing.md)
- [Dokumentationsregeln](/docs/de/developer-guide/documentation-rules.md)

---
_Stand: 2026-06-26 · Status: Stabil_

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

## Linting & Typen

- Backend: **ruff** (Lint) und **mypy** (Typen, Konfiguration in `pyproject.toml`).
- Frontend: **ESLint** (Flat-Config in `eslint.config.js`) plus **`tsc`** im `npm run build`.
  Reine Typprüfung: `npm run typecheck`.

## Doku-Check

```bash
python scripts/check_docs.py        # Struktur, DE/EN-Parität, Manifest, leere Seiten, Links
```
Erzeugt `docs-status.json` + `nav.json`; ist Teil der CI (Job **docs** in `ci.yml`).

## Lokaler Stack

Siehe [Lokales Testen](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).

## Verwandte Seiten

- [Mitwirken](/docs/de/developer-guide/contributing.md)
- [Dokumentationsregeln](/docs/de/developer-guide/documentation-rules.md)

---
_Stand: 2026-06-26 · Status: Stabil_

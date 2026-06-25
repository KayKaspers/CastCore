---
title: "Tests, Linting, Typprüfung"
description: "pytest, ruff, mypy, tsc – lokal und in CI."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Tests, Linting, Typprüfung

> Qualitätssicherung für Backend, Frontend und Doku.

**Zielgruppe:** Entwickler.

## Backend-Tests (pytest)

Unit-Tests (z. B. Command Builder, Security, stream_service) brauchen keine DB/Redis:

```bash
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && pytest -q"
```
Oder mit lokalem Python 3.12: `cd backend && python -m pip install -e ".[dev]" && pytest`.

## Linting & Typen

- Backend: **ruff** (Lint), **mypy** (Typen) – `ruff check .`, `mypy app`.
- Frontend: `npm run build` führt **`tsc -b`** (strikt) vor dem Vite-Build aus.

## Doku-Check

```bash
python scripts/check_docs.py        # Struktur, DE/EN-Parität, Manifest, leere Seiten
```
Erzeugt `docs-status.json` + `nav.json`; läuft in CI
(`.github/workflows/docs-check.yml`).

## Lokaler Stack

Siehe [Lokales Testen](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).

## Verwandte Seiten

- [Mitwirken](/docs/de/developer-guide/contributing.md)
- [Dokumentationsregeln](/docs/de/developer-guide/documentation-rules.md)

---
_Stand: 2026-06-24 · Status: Stabil_

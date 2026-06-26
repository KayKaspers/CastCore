---
title: "Testing, linting, type checks"
description: "pytest, ruff, mypy, tsc – locally and in CI."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-26
---

# Testing, linting, type checks

> Quality assurance for backend, frontend and docs.

**Audience:** developers.

## CI pipeline

The GitHub Actions CI (`.github/workflows/ci.yml`) runs on every push and pull request and
must be green before merge. It has four jobs:

| Job | Checks |
| --- | --- |
| **backend** | `ruff check app` · `mypy` · `pytest -q` |
| **frontend** | `npm ci` · `npm run lint` (ESLint) · `npm run build` (`tsc` + Vite) |
| **docs** | `python scripts/check_docs.py` (structure, DE/EN parity, manifest, internal links) |
| **compose** | `docker compose config` (validates `docker-compose.yml`) |

## Backend tests (pytest)

Unit tests (e.g. command builder, security, stream_service, rate limiting) need no DB/Redis:

```bash
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && ruff check app && mypy && pytest -q"
```
Or with local Python 3.12: `cd backend && python -m pip install -e ".[dev]" && pytest`.

## Linting & types

- Backend: **ruff** (lint) and **mypy** (types, configured in `pyproject.toml`).
- Frontend: **ESLint** (flat config in `eslint.config.js`) plus **`tsc`** inside `npm run
  build`. Types only: `npm run typecheck`.

## Docs check

```bash
python scripts/check_docs.py        # structure, DE/EN parity, manifest, empty pages, links
```
Generates `docs-status.json` + `nav.json`; part of CI (job **docs** in `ci.yml`).

## Local stack

See [Local dev](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).

## Related pages

- [Contributing](/docs/en/developer-guide/contributing.md)
- [Documentation rules](/docs/en/developer-guide/documentation-rules.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

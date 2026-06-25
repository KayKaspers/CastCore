---
title: "Testing, linting, type checks"
description: "pytest, ruff, mypy, tsc – locally and in CI."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Testing, linting, type checks

> Quality assurance for backend, frontend and docs.

**Audience:** developers.

## Backend tests (pytest)

Unit tests (e.g. command builder, security, stream_service) need no DB/Redis:

```bash
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && pytest -q"
```
Or with local Python 3.12: `cd backend && python -m pip install -e ".[dev]" && pytest`.

## Linting & types

- Backend: **ruff** (lint), **mypy** (types) – `ruff check .`, `mypy app`.
- Frontend: `npm run build` runs **`tsc -b`** (strict) before the Vite build.

## Docs check

```bash
python scripts/check_docs.py        # structure, DE/EN parity, manifest, empty pages
```
Generates `docs-status.json` + `nav.json`; runs in CI
(`.github/workflows/docs-check.yml`).

## Local stack

See [Local dev](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).

## Related pages

- [Contributing](/docs/en/developer-guide/contributing.md)
- [Documentation rules](/docs/en/developer-guide/documentation-rules.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

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

## API integration tests

`tests/test_api_*.py` exercise the HTTP layer in-process via httpx **`ASGITransport`** (no
network; the app lifespan — i.e. the Redis loops — is deliberately **not** started).

**DB strategy:** a dedicated PostgreSQL test database **`castcore_test`**, isolated from the
app/dev DB:

- The schema is created once per session via `Base.metadata.create_all`.
- Before each test all tables are truncated and the default roles
  (`admin`/`operator`/`viewer`) are re-seeded.
- The app's `get_db` dependency is overridden to use the test DB.
- Connection comes from the `POSTGRES_*` vars; database name = `TEST_DB_NAME` (default
  `castcore_test`). Rate limiting is disabled in tests.

**External services** are mocked (e.g. the OAuth provider boundary
`oauth_service._post_token` / `fetch_account_name`). No real platform access is required.

Coverage includes: setup status, login/refresh/logout, the 2FA flow, API tokens, RBAC
(admin/operator/viewer), protected routes, stream-job CRUD, command preview (incl. stream-key
masking), preflight, OAuth account status and the monitoring health endpoint.

Locally with CI parity (the container can reach the compose Postgres):

```bash
docker compose exec backend sh -c "pip install -q '.[dev]' && cd /app && pytest -q"
```

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

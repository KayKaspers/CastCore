# Contributing to CastCore

Thanks for working on CastCore. This file defines the workflow and — importantly — the
**documentation rule** that every change must follow.

## The golden rule

> **No feature change without a documentation update.**

If a change touches **code, UI, API, data model, deployment, configuration, security,
CLI, installation or behaviour**, you must check whether documentation is affected and, if
so, update the matching **German and English** pages in the same change. See
[`docs/de/developer-guide/documentation-rules.md`](docs/de/developer-guide/documentation-rules.md).

## Change checklist (use this on every PR)

Copy into the PR description and tick what applies:

```
### Impact
- [ ] UI changed
- [ ] API changed
- [ ] Data model / migration changed
- [ ] Deployment changed
- [ ] Configuration / env vars changed
- [ ] Security changed
- [ ] Feature added
- [ ] Feature removed
- [ ] Error messages / codes changed

### Documentation
- [ ] DE docs updated (docs/de/...)
- [ ] EN docs updated (docs/en/...)
- [ ] Screenshots updated (docs/assets/screenshots/{de,en}/)
- [ ] docs/docs-manifest.json updated
- [ ] `python scripts/check_docs.py` passes (regenerates docs-status.json + nav.json)
- [ ] CHANGELOG.md updated (if relevant)
```

## Definition of Done

A change is complete only when: it works, tests are updated, UI strings are translated
(DE/EN), the affected API/user/admin/developer docs are updated in **both languages**,
`docs-manifest.json` and `docs-status.json` are current, and the changelog is updated if
relevant. (Full list in the documentation rules page.)

## Development

- Local stack & tests: see [`docs/LOCAL_DEV.md`](docs/LOCAL_DEV.md).

### Continuous integration

CI (`.github/workflows/ci.yml`) runs on every push and pull request and must be green
before merge. It runs four jobs — reproduce them locally with the same commands:

**Backend** (`cd backend`, install dev extras once with `pip install -e ".[dev]"`):
- `ruff check app` — lint
- `mypy` — type check (config in `pyproject.toml`)
- `pytest -q` — unit **and** API integration tests. The integration tests need a reachable
  PostgreSQL and use a dedicated `castcore_test` database (connection from the `POSTGRES_*`
  env vars; CI provides a Postgres service). External services (e.g. OAuth providers) are
  mocked.

**Frontend** (`cd frontend`):
- `npm ci` — install from the committed `package-lock.json`
- `npm run lint` — ESLint (flat config in `eslint.config.js`)
- `npm run build` — `tsc` type check + Vite build (`npm run typecheck` for types only)

**Docs**:
- `python scripts/check_docs.py` — structure, DE/EN parity, manifest, links; regenerates
  `docs-status.json` + `nav.json` (commit the result).

**Compose**:
- `docker compose config --quiet` — validates `docker-compose.yml` (needs `SECRET_KEY`,
  `ENCRYPTION_KEY`, `POSTGRES_PASSWORD` set; any value works for validation).

**End-to-end** (separate, manual — `.github/workflows/e2e.yml`, run from the Actions tab):
- `docker compose up -d --build && docker compose exec backend python /app/e2e_stream.py`
  drives the full stream lifecycle (create → preview → start → status → logs → output → stop)
  with a safe local source. Not part of the per-PR `ci` gate (it boots the whole stack).

> No Python/Node on your host? Run the backend checks inside the `backend` container and the
> frontend checks in a throwaway `node:20` container — see [`docs/LOCAL_DEV.md`](docs/LOCAL_DEV.md).

## Git

- Branch off `main`; keep commits focused.
- Conventional, descriptive commit messages.
- Commit/push only what you intend to ship; never commit secrets (`.env` is git-ignored).

## Documentation authoring

- Start new pages from [`docs/templates/`](docs/templates/).
- Every page needs frontmatter (`title`, `description`, `lang`, `audience`, `status`,
  `lastReviewed`) and must exist in **both** `docs/de` and `docs/en`.
- No empty placeholder pages: a stub must still have a real description and a clear TODO.
- No secrets, tokens or real credentials in examples — keep them generic.

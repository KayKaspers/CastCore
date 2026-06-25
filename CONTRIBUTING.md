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
- Backend tests: `pytest` (in the backend container or a local venv).
- Frontend type check + build: `npm run build` (runs `tsc` then `vite build`).
- Docs check: `python scripts/check_docs.py` (or `--strict` to fail on warnings).

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

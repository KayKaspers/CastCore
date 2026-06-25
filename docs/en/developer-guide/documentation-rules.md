---
title: "Documentation rules"
description: "Binding rule: no feature change without a docs update."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Documentation rules

> **Binding for CastCore:** *No feature change without a documentation update.*

**Audience:** developers (including AI assistants).

## The rule

Whenever **code, UI, API, data model, deployment, configuration, security, CLI,
installation or behaviour** changes, check whether documentation is affected. If so, the
corresponding **German and English** documentation files must be updated in the same step.

A change is only **complete** once the related documentation is up to date.

## Definition of done

A change is done only when:

- [ ] Feature works and is tested
- [ ] UI strings are translated (DE/EN)
- [ ] API documentation updated (if affected)
- [ ] User docs **DE** updated (if affected)
- [ ] User docs **EN** updated (if affected)
- [ ] Admin/developer docs updated (if affected)
- [ ] [`docs/docs-manifest.json`](/docs/docs-manifest.json) updated
- [ ] [`docs/docs-status.json`](/docs/docs-status.json) updated (via the check script)
- [ ] `CHANGELOG.md` updated (if relevant)

## Tooling

- **Manifest** `docs/docs-manifest.json`: feature → docs pages, UI routes, API routes,
  models, `lastReviewed`.
- **Status** `docs/docs-status.json`: produced by the check script (current/stale/missing/placeholder).
- **Check script** `scripts/check_docs.py`: validates structure, DE/EN parity, empty
  pages, TODOs, manifest references, stale `lastReviewed` entries.
- **CI** `.github/workflows/docs-check.yml`: runs the check on pull requests.

## DE/EN parity

For **every** page under `docs/de/...` the same page must exist under `docs/en/...` (and
vice versa). German is the maintained primary language; English is kept in parallel. The
check script enforces structural parity.

## Related pages

- [Contributing](/docs/en/developer-guide/contributing.md)
- `CONTRIBUTING.md` (repo root)

---
_Last reviewed: 2026-06-24 · Status: stable_

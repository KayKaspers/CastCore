---
title: "Contributing (developer)"
description: "Workflow, branches, commits, definition of done."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Contributing

> Short version; the authoritative file is
> [`CONTRIBUTING.md`](https://github.com/KayKaspers/CastCore/blob/main/CONTRIBUTING.md).

**Audience:** developers.

## Golden rule

> **No feature change without a documentation update.** Details:
> [Documentation rules](/docs/en/developer-guide/documentation-rules.md).

## Workflow

1. Branch off `main`, focused commits, descriptive messages.
2. Update code + tests; translate UI strings DE/EN.
3. Update affected docs (DE **and** EN), maintain `docs-manifest.json`.
4. `python scripts/check_docs.py` green; `npm run build` and `pytest` green.
5. PR with the **change checklist** from `CONTRIBUTING.md`.

## Definition of done

Feature works · tested · UI translated · API/user/admin/developer docs current (DE+EN) ·
manifest & status updated · changelog updated (if relevant).

## Security & examples

No real secrets/tokens in code, docs or examples – keep them generic.

## Related pages

- [Testing](/docs/en/developer-guide/testing.md) · [Documentation rules](/docs/en/developer-guide/documentation-rules.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

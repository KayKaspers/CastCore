---
title: "Frontend"
description: "React/Vite frontend: structure, state, i18n."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Frontend

> React 18 + TypeScript + Vite + Tailwind, i18next, zustand.

**Audience:** developers.

## Structure

- **`src/pages/`** – one page per route (see `App.tsx`).
- **`src/components/`** – reusable UI (`ui.tsx`, `Layout`, `HelpLink`, `HlsPlayer`,
  `AuthImg`, panels).
- **`src/lib/`** – `api.ts` (fetch + JWT refresh + i18n error codes), `auth.ts` (zustand
  store), `useAsync.ts`, `types.ts`, `helpLinks.ts`.
- **`src/i18n/`** – `de.json`/`en.json` + setup.

## Patterns

- **No** hard-coded text → `t("…")`. Always maintain both DE/EN.
- API via `api.get/post/patch/put/del`; errors are `ApiException` with `.localized`.
- Auth/language state in zustand; token in localStorage, automatic refresh in `api.ts`.
- Branding via Tailwind tokens (Deep Navy/Core Green/…).

## In-app help

`HelpLink page="…md"` links into the `/docs` viewer; the route→docs mapping is in
`lib/helpLinks.ts`.

## Build

`npm run build` (= `tsc -b && vite build`) – `tsc` validates types (strict,
`noUnusedLocals`).

## Related pages

- [Project structure](/docs/en/developer-guide/project-structure.md)
- [Contributing](/docs/en/developer-guide/contributing.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

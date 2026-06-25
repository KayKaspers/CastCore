---
title: "Frontend"
description: "React/Vite-Frontend: Aufbau, State, i18n."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Frontend

> React 18 + TypeScript + Vite + Tailwind, i18next, zustand.

**Zielgruppe:** Entwickler.

## Aufbau

- **`src/pages/`** – eine Seite pro Route (siehe `App.tsx`).
- **`src/components/`** – wiederverwendbare UI (`ui.tsx`, `Layout`, `HelpLink`,
  `HlsPlayer`, `AuthImg`, Panels).
- **`src/lib/`** – `api.ts` (fetch + JWT-Refresh + i18n-Fehlercodes), `auth.ts`
  (zustand-Store), `useAsync.ts`, `types.ts`, `helpLinks.ts`.
- **`src/i18n/`** – `de.json`/`en.json` + Setup.

## Muster

- **Kein** Text hartkodiert → `t("…")`. DE/EN immer beide pflegen.
- API über `api.get/post/patch/put/del`; Fehler sind `ApiException` mit `.localized`.
- Auth-/Sprachzustand in zustand; Token in localStorage, automatischer Refresh in `api.ts`.
- Branding über Tailwind-Tokens (Deep Navy/Core Green/…).

## In-App-Hilfe

`HelpLink page="…md"` verlinkt in den `/docs`-Viewer; die Route→Docs-Zuordnung steht in
`lib/helpLinks.ts`.

## Build

`npm run build` (= `tsc -b && vite build`) – `tsc` validiert Typen (strikt,
`noUnusedLocals`).

## Verwandte Seiten

- [Projektstruktur](/docs/de/developer-guide/project-structure.md)
- [Mitwirken](/docs/de/developer-guide/contributing.md)

---
_Stand: 2026-06-24 · Status: Stabil_

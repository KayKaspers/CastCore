# shared/

Cross-cutting contracts shared between backend and frontend.

Because the backend is Python and the frontend is TypeScript, types are not literally
shared at the source level. Instead:

- The backend exposes **OpenAPI** at `/api/openapi.json`.
- The frontend generates a **typed API client** from that schema (e.g. via
  `openapi-typescript`) into `frontend/src/lib/api/` during build/dev.

This directory holds the source-of-truth artefacts that both sides agree on:

- `error-codes.md` — the canonical list of translatable error codes (kept in sync with
  `backend/app/core/errors.py` and the frontend `error.*` i18n keys).
- `openapi/` — committed snapshots of the OpenAPI schema for client generation in CI.

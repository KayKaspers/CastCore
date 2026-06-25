---
title: "API (developer)"
description: "REST/WS API structure, OpenAPI, typed client."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# API (developer)

> How the API is structured internally. Endpoint reference: [API overview](/docs/en/api/overview.md).

**Audience:** developers.

## Structure

- Versioned under `/api/v1` (`app/api/v1/router.py` aggregates the endpoint routers).
- One router per module in `app/api/v1/endpoints/`.
- Schemas (Pydantic v2) in `app/schemas/`, logic in `app/services/`.

## Auth & roles

- Dependency `get_current_user` (bearer JWT) and the factory `require_roles("operator")`.
- Roles are enforced **server-side** per route.

## Errors

`CastCoreError(code, params=…, http_status=…)` produces
`{detail:{error:{code, params, level}}}` with a **translatable code** (no fixed text).

## OpenAPI

FastAPI generates `/api/openapi.json` and Swagger UI at `/api/docs`. From it you can
generate a **typed client** for the frontend.

## Live

WebSockets under `/api/v1/ws/...` (token via query) – see
[WebSockets / SSE](/docs/en/developer-guide/websocket-sse.md).

## Related pages

- [Backend](/docs/en/developer-guide/backend.md) · [API overview](/docs/en/api/overview.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

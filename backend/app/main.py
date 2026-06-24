"""CastCore backend entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="CastCore API",
    version=__version__,
    summary="Self-Hosted Streaming Operations Suite — Stream. Manage. Control.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# In production the reverse proxy serves the SPA from the same origin; CORS is only
# relaxed for local development against the Vite dev server.
if not settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"name": "CastCore", "version": __version__, "docs": "/api/docs"}

<p align="center">
  <img src="branding/svg/castcore-logo-horizontal-dark.svg" alt="CastCore" width="420">
</p>

<h1 align="center">CastCore</h1>
<p align="center"><strong>Stream. Manage. Control.</strong></p>
<p align="center">Self-Hosted Streaming Operations Suite</p>

---

CastCore is a self-hosted **streaming operations suite** — a control plane for FFmpeg
streams, media sources, network/cloud storage, platform metadata, multi-output
streaming, monitoring, recording and linear channels.

It is **not** "just an FFmpeg web wrapper". CastCore manages sources, analyses media,
plans streams, supervises FFmpeg processes safely, monitors outputs, explains failures
in plain language and offers automatic fallbacks.

> **Positioning:** CastCore is a self-hosted streaming-control suite for managing
> FFmpeg streams, media sources, network & cloud storage, platform metadata,
> multi-destination streaming, monitoring, recording and linear channels.

## Status

🚧 **Early scaffold / Phase 1 in progress.** This repository currently contains the
architecture, project skeleton and the foundations of the backend, frontend, worker and
deployment tooling. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the milestone plan.

## Tech stack

| Layer            | Choice                                                            |
| ---------------- | ----------------------------------------------------------------- |
| Backend / API    | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Pydantic v2        |
| Process manager  | Dedicated asyncio supervisor for long-running FFmpeg processes    |
| Worker           | arq (Redis) for scans, ffprobe, thumbnails, backups               |
| Database         | PostgreSQL 16                                                     |
| Cache / Queue / PubSub | Redis 7                                                     |
| Frontend         | React 18 · TypeScript · Vite · Tailwind · i18next · TanStack Query |
| Reverse proxy    | Caddy (automatic HTTPS)                                           |
| Optional router  | MediaMTX (RTSP/RTMP/SRT/WebRTC/HLS routing)                       |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full rationale.

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env — at minimum set the secret keys and the admin bootstrap values
docker compose up -d
# open https://localhost (or your configured DOMAIN) and complete the Setup Wizard
```

Optional service profiles:

```bash
docker compose --profile mediamtx up -d     # add the MediaMTX media router
docker compose --profile monitoring up -d   # add Prometheus exporters
```

## Native install (no Docker)

```bash
sudo ./scripts/install.sh      # Debian 12 / Ubuntu LTS
sudo ./scripts/update.sh
sudo ./scripts/uninstall.sh
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — strategy, stack, target architecture
- [Data model](docs/DATA_MODEL.md) — entities & relationships
- [API](docs/API.md) — REST + WebSocket surface
- [Deployment](docs/DEPLOYMENT.md) — Docker-first & native install, backup/restore, upgrade
- [Local dev & testing](docs/LOCAL_DEV.md) — run the full stack on Windows via Docker Desktop
- [Security](docs/SECURITY.md) — auth, roles, secret handling, hardening
- [Roadmap](docs/ROADMAP.md) — milestone plan (Phase 1–4)

## Internationalisation

CastCore is fully bilingual (Deutsch / English) from day one. Language is chosen in the
Setup Wizard and per user; no UI strings are hard-coded. Translations live in
`frontend/src/i18n/{de,en}.json`; the backend returns translatable error **codes**.

## License

See [LICENSE](LICENSE). Branding assets in `branding/` follow the CastCore brand guide.

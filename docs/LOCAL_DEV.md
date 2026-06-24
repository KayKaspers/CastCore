# CastCore — Local development & testing

CastCore is Docker-first. On Windows the cleanest path is **Docker Desktop** (WSL2
backend) — it runs the full stack with no local Python/Node.

## 0. One-time prerequisites (Windows, run PowerShell **as Administrator**)

```powershell
wsl --install                          # installs WSL2 + Ubuntu, then REBOOT
winget install -e --id Docker.DockerDesktop
# After install: launch Docker Desktop once, accept terms, wait until it says "running".
```

Virtualization must be enabled in firmware (already confirmed on this machine).

## 1. Start the whole stack

```bash
cp .env.example .env     # (already generated locally with real secrets)
docker compose up -d --build
docker compose ps        # wait until services are healthy
```

The **backend container runs `alembic upgrade head` automatically** on start, so the
schema is created for you. Then:

- App / Setup Wizard: <https://localhost>  (Caddy serves a local self-signed cert —
  accept the browser warning)
- API docs (Swagger): <https://localhost/api/docs>
- First run: complete the Setup Wizard → it creates the admin user.

## 2. Useful commands

```bash
docker compose logs -f backend process-manager     # follow logs
docker compose restart backend
docker compose down                                  # stop (keeps volumes/data)
docker compose down -v                               # stop + WIPE all data volumes
```

Quick API smoke test (after creating the admin in the wizard):

```bash
# bootstrap admin without the UI:
curl -k -X POST https://localhost/api/v1/setup/admin \
  -H 'content-type: application/json' \
  -d '{"username":"admin","password":"changeme123","language":"de"}'

# login:
curl -k -X POST https://localhost/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"username":"admin","password":"changeme123"}'
```

## 3. Running the test suite

Unit tests (Command Builder, security, stream-service argv) need no DB/Redis:

```bash
docker compose run --rm --no-deps backend sh -c "pip install -q '.[dev]' && pytest -q"
```

Or, if you have a real local Python 3.12:

```bash
cd backend && python -m pip install -e ".[dev]" && pytest
```

## 4. Frontend dev server (optional, needs Node 20 locally)

```bash
cd frontend && npm install && npm run dev      # http://localhost:5173 (proxies /api)
```

Otherwise the production SPA is built inside the `frontend` Docker image and served via
Caddy at <https://localhost>.

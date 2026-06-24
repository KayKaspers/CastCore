# CastCore — Deployment

Targets: Debian 12, Ubuntu Server LTS, LXC, VM, bare metal, Proxmox. Assume a clean
Linux system. Two supported paths: **Docker-first** and **native**.

## 1. Docker-first

```bash
git clone https://github.com/KayKaspers/CastCore.git
cd CastCore
cp .env.example .env
# generate secrets:
#   openssl rand -hex 32                                  -> SECRET_KEY
#   python -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())"  -> ENCRYPTION_KEY
# set POSTGRES_PASSWORD, DOMAIN, ACME_EMAIL
docker compose up -d
```

Open `https://<DOMAIN>` and complete the Setup Wizard.

**Services:** `frontend`, `backend`, `process-manager`, `worker`, `postgres`, `redis`,
`caddy`. Optional profiles: `--profile mediamtx`, `--profile monitoring`.

**Persistence (named volumes):** `castcore_pg` (database), `castcore_redis`,
`castcore_data` (media, recordings, logs, backups, mounts, thumbnails),
`castcore_caddy_data/config` (certs).

**Healthchecks & restart:** every service has a healthcheck and `restart: unless-stopped`.
`backend`, `process-manager`, `worker` wait for `postgres`/`redis` to be healthy.

**HTTPS:** Caddy obtains certificates automatically when `DOMAIN` is a public hostname
and `ACME_EMAIL` is set. For `localhost`, Caddy issues a local self-signed cert.

### Mounts inside Docker
SMB/NFS/rclone mounting inside a container needs `cap_add: [SYS_ADMIN]` and (for rclone)
`/dev/fuse`, which weakens isolation. **Preferred:** mount on the host and bind-mount the
path into `castcore_data`. The Setup Wizard and Storage UI surface this tradeoff.

## 2. Native install (no Docker)

```bash
sudo ./scripts/install.sh
```

`install.sh` performs: OS check (Debian/Ubuntu) → apt packages (python3.12, venv,
postgresql, redis, ffmpeg, cifs-utils, nfs-common, rclone, caddy optional) →
create system user `castcore` (no login shell) → create `/opt/castcore` (app),
`/var/lib/castcore` (data), `/var/log/castcore` (logs) with restrictive ownership →
Python venv + deps → PostgreSQL DB/user (or external DB via env) → Redis (or external) →
Alembic migrations → install systemd units → enable & start services → optional Caddy
reverse proxy + HTTPS.

**systemd units:** `castcore-backend.service`, `castcore-process-manager.service`,
`castcore-worker.service`, `castcore-scheduler.service` (see `deploy/systemd/`).

```bash
sudo ./scripts/update.sh      # pull, backup, migrate, restart (rollback note on failure)
sudo ./scripts/uninstall.sh   # stop/disable units, optional purge of data (prompted)
```

## 3. Backup / Restore

- **What:** database, configuration, platform/stream/storage profiles, description
  templates, thumbnails, assets, optionally logs; recordings handled separately.
- **Docker:** `docker compose exec backend castcore-backup create` →
  artifact in `castcore_data:/data/backups`. Restore via UI or
  `castcore-backup restore <file>`.
- **Native:** `castcore-backup` CLI (installed by `install.sh`).
- Optional backup **encryption**; restore shows clear warnings before overwriting.

## 4. Upgrade

1. Read release notes / breaking changes.
2. **Back up** (recommended; `update.sh` does this automatically).
3. Pull new images / code.
4. Run DB migrations (`alembic upgrade head`); migration status shown in UI
   (Settings → Updates). Rollback concept: restore the pre-upgrade backup.

## 5. Reverse proxy examples

- **Caddy** — `deploy/caddy/Caddyfile` (default; automatic HTTPS).
- **Nginx** — `deploy/nginx/castcore.conf` (TLS termination + WebSocket upgrade),
  for operators who already run Nginx.

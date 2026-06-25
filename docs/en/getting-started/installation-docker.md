---
title: "Install with Docker Compose"
description: "Install CastCore with Docker Compose on a fresh Linux system."
lang: en
audience: "Beginners"
status: stable
lastReviewed: 2026-06-24
---

# Install with Docker Compose

> The recommended path. A single command brings up the whole stack.

**Audience:** beginners and administrators.
**Requirements:** Linux host (Debian 12 / Ubuntu LTS recommended), Docker + Docker
Compose, virtualization enabled. See [System requirements](/docs/en/admin-guide/system-requirements.md).

## Step by step

1. **Get the repository**
   ```bash
   git clone https://github.com/KayKaspers/CastCore.git
   cd CastCore
   ```
2. **Create the configuration**
   ```bash
   cp .env.example .env
   ```
3. **Generate secrets** and put them into `.env`:
   ```bash
   openssl rand -hex 32                        # SECRET_KEY (64 hex chars)
   openssl rand -base64 32 | tr '+/' '-_'      # ENCRYPTION_KEY (valid Fernet key)
   ```
   Set `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_PASSWORD` and `DOMAIN`.
4. **Start the stack**
   ```bash
   docker compose up -d --build
   docker compose ps      # wait until services are "healthy"
   ```
   The backend runs the database migration **automatically** on start.
5. **Open** `https://<DOMAIN>` (accept the self-signed certificate for `localhost`) and
   complete the [setup wizard](/docs/en/getting-started/first-setup.md).

## Optional profiles

```bash
docker compose --profile mediamtx up -d      # MediaMTX media router
docker compose --profile monitoring up -d    # monitoring exporters
```

## Notes

> ⚠️ **Never commit secrets.** `.env` is git-ignored. Keep the `ENCRYPTION_KEY` safe and
> separate – without it, encrypted data (stream keys, SMB passwords) is unusable.
> See [Secrets](/docs/en/admin-guide/secrets.md).

> 💡 Prefer mounting SMB/NFS **on the host** and bind-mounting the path into the data
> volume – in-container mounts need elevated privileges.
> See [Storage mounts](/docs/en/admin-guide/storage-mounts.md).

## If something fails

- Containers won't start → [Docker problems](/docs/en/troubleshooting/docker.md)
- HTTPS warnings → [HTTPS / TLS](/docs/en/admin-guide/https.md)

## Related pages

- [Native Linux installation](/docs/en/getting-started/installation-native.md)
- [Operating with Docker Compose](/docs/en/admin-guide/docker-compose.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

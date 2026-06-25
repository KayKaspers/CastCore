---
title: "Native Linux installation"
description: "Set up CastCore without Docker using the install scripts."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Native Linux installation

> Alternative to Docker: install directly on the system via `scripts/install.sh`.

**Audience:** administrators.
**Requirements:** Debian 12 / Ubuntu LTS, root. See
[System requirements](/docs/en/admin-guide/system-requirements.md).

## Install

```bash
git clone https://github.com/KayKaspers/CastCore.git
cd CastCore
sudo ./scripts/install.sh
```

`install.sh` does: OS check · packages (Python 3.12, PostgreSQL, Redis, FFmpeg,
cifs-utils, rclone) · system user `castcore` · directories (`/opt/castcore`,
`/var/lib/castcore`, `/var/log/castcore`) · Python venv · DB/Redis · **generate secrets**
(`/etc/castcore/castcore.env`) · migrations · **systemd services** · optional reverse proxy.

## Services

`castcore-backend`, `castcore-process-manager`, `castcore-worker`, `castcore-scheduler`.

```bash
systemctl status castcore-backend
journalctl -u castcore-backend -f
```

## Update / uninstall

```bash
sudo ./scripts/update.sh       # backup + sync + migrations + restart
sudo ./scripts/uninstall.sh    # remove services (data kept; --purge deletes everything)
```

## Afterwards

Set up reverse proxy/HTTPS ([HTTPS](/docs/en/admin-guide/https.md)), then open the
[setup wizard](/docs/en/getting-started/first-setup.md).

## If something fails

[Native installation (troubleshooting)](/docs/en/troubleshooting/native-installation.md)

## Related pages

- [Install with Docker](/docs/en/getting-started/installation-docker.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

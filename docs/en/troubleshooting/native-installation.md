---
title: "Native installation"
description: "Problems with the native installation."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Native installation

> Help with installing without Docker via `scripts/install.sh`.

**Audience:** administrators.

## Symptom: "Unsupported OS"

`install.sh` supports Debian 12 / Ubuntu LTS. Adapt it for other systems if needed.

## Symptom: packages/FFmpeg missing

**Diagnosis:** `command -v ffmpeg ffprobe`.
**Fix:** `sudo apt install ffmpeg`; set `FFMPEG_PATH`/`FFPROBE_PATH` correctly in
`/etc/castcore/castcore.env`.

## Symptom: systemd service won't start

```bash
systemctl status castcore-backend
journalctl -u castcore-backend -n 50
```
**Common:** DB/Redis unreachable, permission issue on `/var/lib/castcore`.

## Symptom: permission issue on the data directory

Directories are owned by the system user `castcore`:
```bash
sudo chown -R castcore:castcore /var/lib/castcore /var/log/castcore
```

## Symptom: PostgreSQL connection fails

Check the local DB/credentials (created by the installer) or configure an external DB in
`castcore.env`.

## Update / uninstall

```bash
sudo ./scripts/update.sh       # backup + migrations + restart
sudo ./scripts/uninstall.sh    # removes services (data kept; --purge deletes everything)
```

## Related pages

- [Native installation](/docs/en/getting-started/installation-native.md)
- [Logs](/docs/en/admin-guide/logs.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

---
title: "Native Linux-Installation"
description: "CastCore ohne Docker über die Installationsskripte einrichten."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Native Linux-Installation

> Alternative zu Docker: Installation direkt auf dem System via `scripts/install.sh`.

**Zielgruppe:** Administratoren.
**Voraussetzungen:** Debian 12 / Ubuntu LTS, Root-Rechte. Siehe
[Systemanforderungen](/docs/de/admin-guide/system-requirements.md).

## Installation

```bash
git clone https://github.com/KayKaspers/CastCore.git
cd CastCore
sudo ./scripts/install.sh
```

`install.sh` erledigt: OS-Prüfung · Pakete (Python 3.12, PostgreSQL, Redis, FFmpeg,
cifs-utils, rclone) · Systembenutzer `castcore` · Verzeichnisse (`/opt/castcore`,
`/var/lib/castcore`, `/var/log/castcore`) · Python-venv · DB/Redis · **Secrets generieren**
(`/etc/castcore/castcore.env`) · Migrationen · **systemd-Dienste** · optional Reverse Proxy.

## Dienste

`castcore-backend`, `castcore-process-manager`, `castcore-worker`, `castcore-scheduler`.

```bash
systemctl status castcore-backend
journalctl -u castcore-backend -f
```

## Update / Deinstallation

```bash
sudo ./scripts/update.sh       # Backup + Sync + Migrationen + Neustart
sudo ./scripts/uninstall.sh    # Dienste entfernen (Daten bleiben; --purge löscht alles)
```

## Danach

Reverse Proxy/HTTPS einrichten ([HTTPS](/docs/de/admin-guide/https.md)), dann den
[Setup-Assistenten](/docs/de/getting-started/first-setup.md) öffnen.

## Bei Problemen

[Native Installation (Troubleshooting)](/docs/de/troubleshooting/native-installation.md)

## Verwandte Seiten

- [Installation mit Docker](/docs/de/getting-started/installation-docker.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-24 · Status: Stabil_

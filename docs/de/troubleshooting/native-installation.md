---
title: "Native Installation"
description: "Probleme bei der nativen Installation."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Native Installation

> Hilfe bei der Installation ohne Docker über `scripts/install.sh`.

**Zielgruppe:** Administratoren.

## Symptom: „Unsupported OS"

`install.sh` unterstützt Debian 12 / Ubuntu LTS. Auf anderen Systemen ggf. anpassen.

## Symptom: Pakete/FFmpeg fehlen

**Diagnose:** `command -v ffmpeg ffprobe`.
**Lösung:** `sudo apt install ffmpeg`; `FFMPEG_PATH`/`FFPROBE_PATH` in
`/etc/castcore/castcore.env` korrekt setzen.

## Symptom: systemd-Dienst startet nicht

```bash
systemctl status castcore-backend
journalctl -u castcore-backend -n 50
```
**Häufig:** DB/Redis nicht erreichbar, Rechteproblem auf `/var/lib/castcore`.

## Symptom: Rechteproblem auf Datenverzeichnis

Verzeichnisse gehören dem Systembenutzer `castcore`:
```bash
sudo chown -R castcore:castcore /var/lib/castcore /var/log/castcore
```

## Symptom: PostgreSQL-Verbindung scheitert

Lokale DB/Anmeldedaten prüfen (vom Installer angelegt) bzw. externe DB in
`castcore.env` konfigurieren.

## Update / Deinstallation

```bash
sudo ./scripts/update.sh       # Backup + Migrationen + Neustart
sudo ./scripts/uninstall.sh    # entfernt Dienste (Daten bleiben; --purge löscht alles)
```

## Verwandte Seiten

- [Native Installation](/docs/de/getting-started/installation-native.md)
- [Logs](/docs/de/admin-guide/logs.md)

---
_Stand: 2026-06-24 · Status: Stabil_

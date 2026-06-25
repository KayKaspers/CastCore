---
title: "Konfiguration"
description: "Alle Konfigurationsoptionen im Überblick."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Konfiguration

> Überblick, **wo** CastCore konfiguriert wird.

**Zielgruppe:** Administratoren.

## Ebenen

| Ebene | Was | Wo |
| --- | --- | --- |
| **Umgebung** | Secrets, DB/Redis, Pfade, Domain, FFmpeg-Pfade | `.env` (Docker) bzw. `/etc/castcore/castcore.env` (nativ) |
| **Instanz** | Instanzname, Standardsprache | UI → Einstellungen (Admin) |
| **Pro Benutzer** | Sprache | UI → Einstellungen |
| **Fachlich** | Profile, Ziele, Quellen, Channels, Benachrichtigungen, Scheduler | UI / API |

## Umgebungsvariablen

Vollständige Referenz: [Umgebungsvariablen](/docs/de/reference/environment-variables.md).
Wichtig: `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_*`, `REDIS_*`, `DOMAIN`, `DATA_DIR`,
`FFMPEG_PATH`/`FFPROBE_PATH`.

## Instanz- & Benutzereinstellungen

Siehe [Einstellungen](/docs/de/user-guide/settings.md).

## Hinweise

> 🔐 Secrets gehören in die Umgebung, **nicht** ins Repo. Die `.env` ist git-ignoriert.

## Verwandte Seiten

- [Umgebungsvariablen](/docs/de/reference/environment-variables.md) · [Secrets](/docs/de/admin-guide/secrets.md)

---
_Stand: 2026-06-24 · Status: Stabil_

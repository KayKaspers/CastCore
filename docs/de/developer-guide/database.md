---
title: "Datenbank"
description: "PostgreSQL-Schema und SQLAlchemy-Modelle."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Datenbank

> PostgreSQL 16, Zugriff über SQLAlchemy 2 (async, asyncpg). Migrationen via Alembic.

**Zielgruppe:** Entwickler. Vollständiges Modell:
[`docs/DATA_MODEL.md`](https://github.com/KayKaspers/CastCore/blob/main/docs/DATA_MODEL.md).

## Konventionen

- Alle Tabellen: `id` (UUID), `created_at`, `updated_at` (Timestamp-Mixin).
- Modelle in `app/models/`, in `app/models/__init__.py` registriert (für Alembic).
- Verschlüsselte Spalten (Stream-Keys, SMB-Passwörter) speichern **Ciphertext**.

## Wichtige Tabellen (Auszug)

- Security: `users`, `roles`, `user_roles`, `sessions`, `api_tokens`, `audit_events`.
- Streaming: `stream_jobs`, `ffmpeg_profiles`, `inputs`, `outputs`, `destinations`,
  `process_status`.
- Medien/Channels: `storage_sources`, `smb_sources`, `media_library_items`,
  `media_probe_data`, `playlists`, `playlist_items`, `channels`.
- Plattform/Assets: `platform_metadata`, `assets`.
- Betrieb: `settings`, `setup_state`, `scheduler_entries`, `notifications`,
  `recordings`, `backups`.

## Relationen-Hinweise

Ein **stream_job** hat viele `inputs`/`outputs`; jeder `output` → `destination`.
`process_status` ist pro Output. `storage_sources` ist die polymorphe Wurzel
(SMB-Detail in `smb_sources`).

## Verwandte Seiten

- [Migrationen](/docs/de/developer-guide/migrations.md)

---
_Stand: 2026-06-24 · Status: Stabil_

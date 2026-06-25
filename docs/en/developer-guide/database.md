---
title: "Database"
description: "PostgreSQL schema and SQLAlchemy models."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Database

> PostgreSQL 16, accessed via SQLAlchemy 2 (async, asyncpg). Migrations via Alembic.

**Audience:** developers. Full model:
[`docs/DATA_MODEL.md`](https://github.com/KayKaspers/CastCore/blob/main/docs/DATA_MODEL.md).

## Conventions

- All tables: `id` (UUID), `created_at`, `updated_at` (timestamp mixin).
- Models in `app/models/`, registered in `app/models/__init__.py` (for Alembic).
- Encrypted columns (stream keys, SMB passwords) store **ciphertext**.

## Key tables (excerpt)

- Security: `users`, `roles`, `user_roles`, `sessions`, `api_tokens`, `audit_events`.
- Streaming: `stream_jobs`, `ffmpeg_profiles`, `inputs`, `outputs`, `destinations`,
  `process_status`.
- Media/channels: `storage_sources`, `smb_sources`, `media_library_items`,
  `media_probe_data`, `playlists`, `playlist_items`, `channels`.
- Platform/assets: `platform_metadata`, `assets`.
- Operations: `settings`, `setup_state`, `scheduler_entries`, `notifications`,
  `recordings`, `backups`.

## Relationship notes

A **stream_job** has many `inputs`/`outputs`; each `output` → `destination`.
`process_status` is per output. `storage_sources` is the polymorphic root (SMB detail in
`smb_sources`).

## Related pages

- [Migrations](/docs/en/developer-guide/migrations.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

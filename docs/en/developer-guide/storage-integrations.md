---
title: "Storage integrations"
description: "Source/mount layer and how to extend it."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Storage integrations

> Structure of the source/mount layer and how to add new source types.

**Audience:** developers.

## Model

- `storage_sources` is the **polymorphic root** (`class`/`type`, status, path).
- Type detail in dedicated tables, e.g. `smb_sources` (server/share/creds/mount path).
- Logic in `app/services/storage_service.py`.

## Security

- Secrets (SMB password) **encrypted**; mount credentials in `0600` files.
- External commands (`mount.cifs`, `umount`) as an **argument list** (no shell).
- `browse` is **traversal-protected** (confined to the effective path).

## Adding a source type

1. Create a detail table + migration, attached to the `storage_sources` type.
2. Extend `storage_service`: `effective_path`, `test_source`, and `mount`/`unmount` if
   applicable.
3. Add endpoints/schemas and UI ([Sources](/docs/en/user-guide/sources-storage.md)).
4. Update the docs (DE+EN) + manifest.

## Note

Container mounts need elevated privileges – prefer
[host mounts](/docs/en/admin-guide/storage-mounts.md).

## Related pages

- [API: sources](/docs/en/api/sources.md) · [Storage mounts](/docs/en/admin-guide/storage-mounts.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

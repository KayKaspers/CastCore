---
title: "Storage mounts"
description: "Host vs. container mounts and data directories."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Storage mounts

> Where CastCore stores data and how to best attach network storage (SMB/NFS).

**Audience:** administrators.

## Data directories

Everything lives under `DATA_DIR` (default `/data`, the Docker volume `castcore_data`):

| Path | Content |
| --- | --- |
| `/data/media` | media sources |
| `/data/recordings` | recordings |
| `/data/logs` | logs |
| `/data/backups` | backups |
| `/data/mounts` | mount points for network sources |
| `/data/thumbnails` | assets/thumbnails |

## Host mount vs. container mount (important)

> ⚠️ **Recommendation: mount on the host.** Mounting **inside** the container needs
> elevated privileges (`CAP_SYS_ADMIN`, possibly `/dev/fuse`), which weakens isolation.

**Recommended approach:**

1. Mount the network share on the **host** (e.g. via `/etc/fstab`).
2. Bind-mount the host path into the data volume, or add it as a **local source** in
   CastCore.

This keeps the container unprivileged and mounting robust.

## In-container mount (only if needed)

If CastCore should mount itself (SMB/rclone), the container must be granted the required
capabilities. This is deliberately **not** the default. See
[SMB / CIFS](/docs/en/admin-guide/smb-cifs.md).

## Related pages

- [SMB / CIFS](/docs/en/admin-guide/smb-cifs.md) · [NFS](/docs/en/admin-guide/nfs.md)
- [Sources / storage](/docs/en/user-guide/sources-storage.md)
- [SMB problems](/docs/en/troubleshooting/smb-problems.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

---
title: "Cloud sources"
description: "Prepare S3/WebDAV/rclone remotes as sources."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Cloud sources

> Cloud storage (S3, WebDAV, Nextcloud, B2, R2, Google Drive, Dropbox, OneDrive) as a
> source.

**Audience:** administrators.

> ℹ️ **Status:** cloud integration is modularly **prepared** but not yet implemented in the
> UI. Until then, mount cloud remotes via **rclone mount** on the host and use them as a
> [local source](/docs/en/user-guide/sources-storage.md).

## Interim: rclone mount (host)

```bash
rclone mount myremote:bucket /mnt/castcore-cloud \
  --vfs-cache-mode full --read-only --daemon
```
Then add `/mnt/castcore-cloud` as a **local source** in CastCore.

## Planned integration

Test connection · store OAuth/API credentials **encrypted** · browse the remote · cache
directory · sync or mount mode · resilience for unstable links/large files.

## Notes

> 💡 Cloud connections can be unstable – `--vfs-cache-mode full` and generous buffers help
> with large media files.

## Related pages

- [Storage mounts](/docs/en/admin-guide/storage-mounts.md) · [Sources / storage](/docs/en/user-guide/sources-storage.md)

---
_Last reviewed: 2026-06-24 · Status: stable (feature in preparation)_

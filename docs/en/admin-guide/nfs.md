---
title: "NFS"
description: "Use NFS exports as a source."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# NFS

> Use NFS shares as a media source.

**Audience:** administrators.

## Recommended: host mount

Best to mount NFS on the **host** and add the path as a **local source** in CastCore –
like [SMB](/docs/en/admin-guide/smb-cifs.md), this keeps the container unprivileged.

```bash
# /etc/fstab (generic example)
server:/export/media  /mnt/castcore-nfs  nfs  ro,soft,timeo=30  0  0
```

Then create a local source with the mount path under **Sources**.

## Notes

> 💡 For stable streams set `soft` + `timeo` so stalls on network issues stay bounded.
> Read-only (`ro`) is sufficient for sources.

> ℹ️ Native NFS management **in the UI** is prepared but not yet implemented – mount via
> the host for now.

## Related pages

- [Storage mounts](/docs/en/admin-guide/storage-mounts.md) · [SMB / CIFS](/docs/en/admin-guide/smb-cifs.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

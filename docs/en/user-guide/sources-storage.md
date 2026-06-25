---
title: "Sources / storage"
description: "Create, test, mount and browse local and network (SMB) sources."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Sources / storage

> Sources provide the media for streams and channels: local folders and SMB shares.

**Audience:** users / operators. UI area: **Sources / storage** (`/sources`).

## Create a local source

Name + path (e.g. `/data/media`). On create, reachability is checked (status
**online/error**).

## Create an SMB source

Name, server/IP, share, optional domain/user/password. **Test connection** checks TCP 445.
Details/mount topic: [SMB / CIFS](/docs/en/admin-guide/smb-cifs.md).

## Actions

| Action | Effect |
| --- | --- |
| **Test** | Check reachability (refresh status) |
| **mount / unmount** | Mount/unmount SMB (needs privileges, see below) |
| **Browse** | Browse a directory; **"copy path"** copies the absolute path |
| **✕** | Delete the source |

## From source to stream

1. **Browse** → on a file click **"copy path"**.
2. Paste the path in the [stream editor](/docs/en/user-guide/stream-editor.md) as the input
   URI, or scan the source in the [media library](/docs/en/user-guide/media-library.md).

## Notes

> 🔐 SMB passwords are stored encrypted; browsing is **traversal-protected** (confined to
> the source path).

> ⚠️ Container mounts need elevated privileges – prefer
> [mounting on the host](/docs/en/admin-guide/storage-mounts.md).

## If something fails

[SMB problems](/docs/en/troubleshooting/smb-problems.md)

## Related pages

- [Media library](/docs/en/user-guide/media-library.md) · [Storage mounts](/docs/en/admin-guide/storage-mounts.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

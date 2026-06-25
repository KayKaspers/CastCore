---
title: "SMB / CIFS"
description: "Mount SMB shares securely (credentials, mounts)."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# SMB / CIFS

> Use SMB/CIFS shares as a source – securely and accountably.

**Audience:** administrators.

## Create in CastCore

**Sources** area → SMB source: display name, server/IP, share, optional domain/workgroup,
user, password, SMB version, read-only. **Test connection** checks reachability (TCP 445).

> 🔐 The password is stored **encrypted** and only written to a `0600` credentials file –
> never on the command line, never in logs.

## Host mount (recommended)

Mounting inside the container needs elevated privileges. Better to mount on the **host**:

```bash
# /etc/fstab (generic example)
//server/share  /mnt/castcore-share  cifs  credentials=/etc/castcore/smb.cred,ro,iocharset=utf8,vers=3.0  0  0
```
Then use the host path as a **local source** in CastCore. See
[Storage mounts](/docs/en/admin-guide/storage-mounts.md).

## Container mount (only if needed)

Requires `cap_add: [SYS_ADMIN]` on the container (deliberately not the default). Otherwise
the mount fails with "Unable to apply new capability set".

## If something fails

[SMB problems](/docs/en/troubleshooting/smb-problems.md)

## Related pages

- [NFS](/docs/en/admin-guide/nfs.md) · [Sources / storage](/docs/en/user-guide/sources-storage.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

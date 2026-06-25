---
title: "SMB problems"
description: "Resolve SMB mount and access errors."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-24
---

# SMB problems

> Use this page when an SMB/CIFS source is unreachable or the mount fails.

**Audience:** operators / administrators.

## Symptom: "… :445 unreachable" (connection test fails)

**Causes:** wrong server/IP, firewall, port 445 blocked, server offline.
**Diagnosis:**
```bash
nc -vz <server> 445        # test reachability
```
**Fix:** verify server/IP and network; the share must support SMB2/3.

## Symptom: "Unable to apply new capability set" when mounting in the container

**Cause:** mounting **inside** the container needs elevated privileges (`CAP_SYS_ADMIN`),
which are not granted by default.
**Fix (recommended):** mount on the **host** and bind-mount the path into the data volume:
```bash
# /etc/fstab (generic example)
//server/share  /mnt/castcore-share  cifs  credentials=/etc/castcore/smb.cred,ro,iocharset=utf8  0  0
```
Then add the host path as a **local source** in CastCore. See
[Storage mounts](/docs/en/admin-guide/storage-mounts.md).

## Symptom: "Permission denied" / login fails

**Causes:** wrong credentials, wrong domain/workgroup, expired password.
**Fix:** re-save the credentials in the source (stored encrypted). Leave the domain empty
or set it correctly.

## Security

> 🔐 Credentials are stored **encrypted** and only written to a `0600` credentials file –
> never on the command line, never in logs. See [Secrets](/docs/en/admin-guide/secrets.md).

## Relevant logs

```bash
dmesg | tail            # CIFS kernel messages (host)
docker compose logs backend
```

## Related pages

- [SMB / CIFS](/docs/en/admin-guide/smb-cifs.md)
- [Sources / storage](/docs/en/user-guide/sources-storage.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

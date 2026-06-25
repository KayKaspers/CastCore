---
title: "SMB / CIFS"
description: "SMB-Freigaben sicher einbinden (Credentials, Mounts)."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# SMB / CIFS

> SMB/CIFS-Freigaben als Quelle einbinden – sicher und nachvollziehbar.

**Zielgruppe:** Administratoren.

## In CastCore anlegen

Bereich **Quellen** → SMB-Quelle: Anzeigename, Server/IP, Freigabe, optional
Domain/Workgroup, Benutzer, Passwort, SMB-Version, Read-only. **Verbindung testen** prüft
die Erreichbarkeit (TCP 445).

> 🔐 Das Passwort wird **verschlüsselt** gespeichert und nur in eine `0600`-Credentials-Datei
> geschrieben – nie auf der Kommandozeile, nie im Log.

## Host-Mount (empfohlen)

Mounten im Container braucht erweiterte Rechte. Besser auf dem **Host** mounten:

```bash
# /etc/fstab (Beispiel, generisch)
//server/freigabe  /mnt/castcore-share  cifs  credentials=/etc/castcore/smb.cred,ro,iocharset=utf8,vers=3.0  0  0
```
Danach den Host-Pfad als **lokale Quelle** in CastCore nutzen. Siehe
[Storage-Mounts](/docs/de/admin-guide/storage-mounts.md).

## Container-Mount (nur wenn nötig)

Erfordert `cap_add: [SYS_ADMIN]` am Container (bewusst nicht Standard). Andernfalls
scheitert der Mount mit „Unable to apply new capability set".

## Bei Problemen

[SMB-Probleme](/docs/de/troubleshooting/smb-problems.md)

## Verwandte Seiten

- [NFS](/docs/de/admin-guide/nfs.md) · [Quellen / Storage](/docs/de/user-guide/sources-storage.md)

---
_Stand: 2026-06-24 · Status: Stabil_

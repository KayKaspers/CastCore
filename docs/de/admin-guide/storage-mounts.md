---
title: "Storage-Mounts"
description: "Host- vs. Container-Mounts und Datenverzeichnisse."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Storage-Mounts

> Wo CastCore Daten ablegt und wie Netzwerk-Storage (SMB/NFS) am besten eingebunden wird.

**Zielgruppe:** Administratoren.

## Datenverzeichnisse

Alles liegt unter `DATA_DIR` (Standard `/data`, im Docker-Volume `castcore_data`):

| Pfad | Inhalt |
| --- | --- |
| `/data/media` | Medienquellen |
| `/data/recordings` | Aufnahmen |
| `/data/logs` | Logs |
| `/data/backups` | Backups |
| `/data/mounts` | Mountpunkte für Netzwerkquellen |
| `/data/thumbnails` | Assets/Thumbnails |

## Host-Mount vs. Container-Mount (wichtig)

> ⚠️ **Empfehlung: auf dem Host mounten.** Mounten **innerhalb** des Containers braucht
> erweiterte Rechte (`CAP_SYS_ADMIN`, ggf. `/dev/fuse`), was die Isolation schwächt.

**Empfohlener Weg:**

1. Netzwerkfreigabe auf dem **Host** mounten (z. B. via `/etc/fstab`).
2. Den Host-Pfad in das Daten-Volume bind-mounten oder als **lokale Quelle** in CastCore
   anlegen.

So bleibt der Container unprivilegiert und das Mounten ist robust.

## In-Container-Mount (nur wenn nötig)

Soll CastCore selbst mounten (SMB/rclone), müssen dem Container die nötigen Capabilities
gegeben werden. Das ist bewusst **nicht** Standard. Siehe
[SMB / CIFS](/docs/de/admin-guide/smb-cifs.md).

## Verwandte Seiten

- [SMB / CIFS](/docs/de/admin-guide/smb-cifs.md) · [NFS](/docs/de/admin-guide/nfs.md)
- [Quellen / Storage](/docs/de/user-guide/sources-storage.md)
- [SMB-Probleme](/docs/de/troubleshooting/smb-problems.md)

---
_Stand: 2026-06-24 · Status: Stabil_

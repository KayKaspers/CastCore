---
title: "NFS"
description: "NFS-Exporte als Quelle einbinden."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# NFS

> NFS-Freigaben als Medienquelle nutzen.

**Zielgruppe:** Administratoren.

## Empfohlener Weg: Host-Mount

NFS am besten auf dem **Host** mounten und den Pfad als **lokale Quelle** in CastCore
einbinden – wie bei [SMB](/docs/de/admin-guide/smb-cifs.md) bleibt der Container
unprivilegiert.

```bash
# /etc/fstab (Beispiel, generisch)
server:/export/media  /mnt/castcore-nfs  nfs  ro,soft,timeo=30  0  0
```

Danach unter **Quellen** eine lokale Quelle mit dem Mount-Pfad anlegen.

## Hinweise

> 💡 Für stabile Streams: `soft` + `timeo` setzen, damit Hänger bei Netzwerkproblemen
> begrenzt bleiben. Read-only (`ro`) genügt für Quellen.

> ℹ️ Eine native NFS-Verwaltung **in der UI** ist vorbereitet, aber noch nicht
> implementiert – aktuell über den Host mounten.

## Verwandte Seiten

- [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md) · [SMB / CIFS](/docs/de/admin-guide/smb-cifs.md)

---
_Stand: 2026-06-24 · Status: Stabil_

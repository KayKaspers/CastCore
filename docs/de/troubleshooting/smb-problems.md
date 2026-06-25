---
title: "SMB-Probleme"
description: "SMB-Mount- und Zugriffsfehler lösen."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# SMB-Probleme

> Diese Seite hilft, wenn eine SMB/CIFS-Quelle nicht erreichbar ist oder der Mount fehlschlägt.

**Zielgruppe:** Operatoren / Administratoren.

## Symptom: „… :445 unreachable" (Verbindungstest schlägt fehl)

**Ursachen:** Server/IP falsch, Firewall, Port 445 blockiert, Server offline.
**Diagnose:**
```bash
nc -vz <server> 445        # Erreichbarkeit testen
```
**Lösung:** Server/IP und Netzwerk prüfen; Freigabe muss SMB2/3 unterstützen.

## Symptom: „Unable to apply new capability set" beim Mount im Container

**Ursache:** Mounten **innerhalb** des Containers braucht erweiterte Rechte
(`CAP_SYS_ADMIN`), die standardmäßig nicht gesetzt sind.
**Lösung (empfohlen):** Auf dem **Host** mounten und den Pfad ins Daten-Volume einbinden:
```bash
# /etc/fstab (Beispiel, generisch)
//server/freigabe  /mnt/castcore-share  cifs  credentials=/etc/castcore/smb.cred,ro,iocharset=utf8  0  0
```
Danach den Host-Pfad als **lokale Quelle** in CastCore anlegen. Siehe
[Storage-Mounts](/docs/de/admin-guide/storage-mounts.md).

## Symptom: „Permission denied" / Login schlägt fehl

**Ursachen:** Falsche Zugangsdaten, falsche Domain/Workgroup, abgelaufenes Passwort.
**Lösung:** Zugangsdaten in der Quelle neu speichern (werden verschlüsselt abgelegt).
Domain ggf. leer lassen oder korrekt setzen.

## Sicherheit

> 🔐 Zugangsdaten werden **verschlüsselt** gespeichert und nur in eine
> `0600`-Credentials-Datei geschrieben – nie auf der Kommandozeile, nie im Log.
> Siehe [Secrets](/docs/de/admin-guide/secrets.md).

## Relevante Logs

```bash
dmesg | tail            # CIFS-Kernelmeldungen (Host)
docker compose logs backend
```

## Verwandte Seiten

- [SMB / CIFS](/docs/de/admin-guide/smb-cifs.md)
- [Quellen / Storage](/docs/de/user-guide/sources-storage.md)

---
_Stand: 2026-06-24 · Status: Stabil_

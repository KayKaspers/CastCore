---
title: "Secrets-Verwaltung"
description: "Verschlüsselung (Fernet), ENCRYPTION_KEY, Schlüsselrotation."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Secrets-Verwaltung

> CastCore speichert sensible Daten (Stream-Keys, SMB-/OAuth-Zugangsdaten,
> Benachrichtigungs-Secrets) **verschlüsselt**.

**Zielgruppe:** Administratoren.

## Schlüssel

| Variable | Zweck |
| --- | --- |
| `SECRET_KEY` | Signiert JWT-Token. 64 Hex-Zeichen. |
| `ENCRYPTION_KEY` | **Fernet-Schlüssel** zur Verschlüsselung gespeicherter Secrets. |

Generieren:
```bash
openssl rand -hex 32                     # SECRET_KEY
openssl rand -base64 32 | tr '+/' '-_'   # ENCRYPTION_KEY (gültiger Fernet-Key)
```

## Eigenschaften

- Secrets werden **at-rest** mit Fernet verschlüsselt.
- Über die API sind sie **write-only**: bei Eingabe akzeptiert, nach außen **maskiert**
  (z. B. `••••1234`) bzw. nur als „vorhanden" angezeigt.
- Secrets erscheinen **nie** im Log; Command-Vorschauen maskieren Stream-Keys in URLs.

## Wichtig: ENCRYPTION_KEY sichern

> 🔐 **Ohne den `ENCRYPTION_KEY` sind verschlüsselte Daten unbrauchbar.** Bewahre ihn
> sicher **und getrennt** von den Backups auf. Ein logisches Backup enthält die Secrets
> nur **verschlüsselt** – die Wiederherstellung benötigt denselben Schlüssel.

## Schlüsselrotation

Ein Wechsel des `ENCRYPTION_KEY` macht bestehende verschlüsselte Werte unlesbar. Plane
eine Rotation nur mit Re-Verschlüsselung der betroffenen Felder (zukünftiges Werkzeug).

## Verwandte Seiten

- [Security Best Practices](/docs/de/admin-guide/security.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-24 · Status: Stabil_

---
title: "Installation mit Docker Compose"
description: "CastCore mit Docker Compose auf einem frischen Linux-System installieren."
lang: de
audience: "Einsteiger"
status: stable
lastReviewed: 2026-06-24
---

# Installation mit Docker Compose

> Der empfohlene Weg. Ein einziger Befehl bringt den kompletten Stack hoch.

**Zielgruppe:** Einsteiger und Administratoren.
**Voraussetzungen:** Linux-Host (Debian 12 / Ubuntu LTS empfohlen), Docker + Docker Compose,
Virtualisierung aktiviert. Siehe [Systemanforderungen](/docs/de/admin-guide/system-requirements.md).

## Schritt für Schritt

1. **Repository holen**
   ```bash
   git clone https://github.com/KayKaspers/CastCore.git
   cd CastCore
   ```
2. **Konfiguration anlegen**
   ```bash
   cp .env.example .env
   ```
3. **Secrets generieren** und in `.env` eintragen:
   ```bash
   # 64 Hex-Zeichen
   openssl rand -hex 32
   # gültiger Fernet-Key (für verschlüsselte Secrets)
   openssl rand -base64 32 | tr '+/' '-_'
   ```
   Setze `SECRET_KEY`, `ENCRYPTION_KEY`, `POSTGRES_PASSWORD` und `DOMAIN`.
4. **Stack starten**
   ```bash
   docker compose up -d --build
   docker compose ps      # warten, bis alle Services "healthy" sind
   ```
   Das Backend führt die Datenbank-Migration beim Start **automatisch** aus.
5. **Öffnen**: `https://<DOMAIN>` (bei `localhost` Self-Signed-Zertifikat akzeptieren)
   und den [Setup-Assistenten](/docs/de/getting-started/first-setup.md) durchlaufen.

## Optionale Profile

```bash
docker compose --profile mediamtx up -d      # MediaMTX Media-Router
docker compose --profile monitoring up -d    # Monitoring-Exporter
```

## Hinweise

> ⚠️ **Secrets niemals committen.** Die `.env` ist git-ignoriert. Bewahre den
> `ENCRYPTION_KEY` sicher und getrennt auf – ohne ihn sind verschlüsselte Daten
> (Stream-Keys, SMB-Passwörter) unbrauchbar. Siehe [Secrets](/docs/de/admin-guide/secrets.md).

> 💡 SMB/NFS am besten **auf dem Host** mounten und ins Daten-Volume einbinden –
> Mounts im Container brauchen erweiterte Rechte. Siehe [Storage-Mounts](/docs/de/admin-guide/storage-mounts.md).

## Bei Problemen

- Container starten nicht → [Docker-Probleme](/docs/de/troubleshooting/docker.md)
- HTTPS-Warnungen → [HTTPS / TLS](/docs/de/admin-guide/https.md)

## Verwandte Seiten

- [Native Linux-Installation](/docs/de/getting-started/installation-native.md)
- [Docker-Compose-Betrieb](/docs/de/admin-guide/docker-compose.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-24 · Status: Stabil_

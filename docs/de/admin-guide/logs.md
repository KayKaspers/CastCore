---
title: "Logs"
description: "Wo CastCore-Logs liegen und wie man sie liest."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Logs

> CastCore bietet mehrere Log-Ebenen: Dienst-Logs, Live-FFmpeg-Logs und das Audit-Log.

**Zielgruppe:** Administratoren.

## Dienst-Logs (Docker)

```bash
docker compose logs -f backend            # API + Hintergrund-Loops
docker compose logs -f process-manager    # FFmpeg-Supervisor
docker compose logs -f worker             # Async-Jobs
docker compose logs -f caddy postgres redis
```

## Dienst-Logs (nativ)

```bash
journalctl -u castcore-backend -f
journalctl -u castcore-process-manager -f
```
Zusätzlich: `/var/log/castcore` (nativ) bzw. `/data/logs` (Daten-Volume).

## Live-FFmpeg-Logs

Pro Stream-Job im UI über **Live-Logs** – inkl. Klartext-Hinweisen
(Stream-Health-Assistant) und Verlinkung zur passenden
[Fehlerhilfe](/docs/de/troubleshooting/ffmpeg-errors.md).

## Audit-Log

Sicherheitsrelevante Aktionen (Login, Start/Stop, Backup, Benutzer) findest du unter
`/audit`. Siehe [Security](/docs/de/admin-guide/security.md).

## Hinweise

> 🔐 In Logs landen **keine** Secrets; Stream-Keys sind maskiert.

## Verwandte Seiten

- [Monitoring](/docs/de/user-guide/monitoring.md)
- [Troubleshooting](/docs/de/troubleshooting/index.md)

---
_Stand: 2026-06-24 · Status: Stabil_

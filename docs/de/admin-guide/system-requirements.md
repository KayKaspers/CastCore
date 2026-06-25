---
title: "Systemanforderungen"
description: "Hardware-, OS- und Netzwerk-Voraussetzungen für CastCore."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-24
---

# Systemanforderungen

> Was der Zielserver mitbringen sollte.

**Zielgruppe:** Administratoren.

## Betriebssystem

Debian 12 oder Ubuntu Server LTS (auch LXC, VM, Bare Metal, Proxmox). Für Docker:
aktivierte Virtualisierung.

## Hardware (Richtwerte)

| Last | CPU | RAM | Hinweis |
| --- | --- | --- | --- |
| 1 Stream (copy) | 2 Kerne | 2 GB | minimal |
| 1–2 Re-Encodes 1080p | 4 Kerne | 4 GB | x264 `veryfast` |
| Mehrere Streams / Channels | 8+ Kerne | 8+ GB | oder GPU-Encoder |

**GPU** (optional): NVIDIA (NVENC), Intel (QSV) oder VAAPI für effizientes Encoding –
Treiber/Geräte müssen ins System bzw. den Container durchgereicht werden.

## Speicher & Netzwerk

- Genug Platz für Medien/Recordings unter `DATA_DIR`.
- Stabile **Upload-Bandbreite** für die Zielbitrate(n); Multi-Output addiert sich.

## Software

Docker + Docker Compose (Docker-Weg) **oder** die vom Installer verwalteten Pakete
(nativer Weg). FFmpeg/ffprobe bringt CastCore mit bzw. installiert sie.

## Verwandte Seiten

- [Deployment](/docs/de/admin-guide/deployment.md) · [Performance](/docs/de/troubleshooting/performance.md)

---
_Stand: 2026-06-24 · Status: Stabil_

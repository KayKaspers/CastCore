---
title: "System requirements"
description: "Hardware, OS and network requirements for CastCore."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-24
---

# System requirements

> What the target server should provide.

**Audience:** administrators.

## Operating system

Debian 12 or Ubuntu Server LTS (also LXC, VM, bare metal, Proxmox). For Docker:
virtualization enabled.

## Hardware (guidelines)

| Load | CPU | RAM | Note |
| --- | --- | --- | --- |
| 1 stream (copy) | 2 cores | 2 GB | minimal |
| 1–2 re-encodes 1080p | 4 cores | 4 GB | x264 `veryfast` |
| Several streams / channels | 8+ cores | 8+ GB | or GPU encoders |

**GPU** (optional): NVIDIA (NVENC), Intel (QSV) or VAAPI for efficient encoding – drivers/
devices must be passed into the system or container.

## Storage & network

- Enough space for media/recordings under `DATA_DIR`.
- Stable **upload bandwidth** for the target bitrate(s); multi-output adds up.

## Software

Docker + Docker Compose (Docker path) **or** the installer-managed packages (native path).
CastCore brings or installs FFmpeg/ffprobe.

## Related pages

- [Deployment](/docs/en/admin-guide/deployment.md) · [Performance](/docs/en/troubleshooting/performance.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

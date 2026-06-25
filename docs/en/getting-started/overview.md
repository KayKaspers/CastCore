---
title: "What is CastCore?"
description: "Overview of CastCore's purpose, audience and capabilities."
lang: en
audience: "Beginners"
status: stable
lastReviewed: 2026-06-24
---

# What is CastCore?

> CastCore is a **self-hosted streaming operations suite** – a control plane for FFmpeg
> streams, media sources, storage, platform metadata, multi-output streaming, monitoring,
> recording and linear channels.

**Audience:** beginners and decision makers.

## Who is CastCore for?

- **Streamers & creators** publishing to several platforms at once.
- **Clubs, broadcasters, communities** running their own 24/7 channels.
- **Administrators** who want centralized, secure, auditable streaming.

## What can CastCore do?

- **Stream jobs**: create, start, stop and monitor FFmpeg streams safely.
- **Multi-output**: one stream → many destinations (Twitch, YouTube, own RTMP, recording).
- **Sources & storage**: local files, SMB/CIFS, later NFS/cloud.
- **Media library**: scan sources, analyse via ffprobe, pick as input.
- **Channels**: linear 24/7 channels from playlists with HLS output, EPG and M3U.
- **Platform metadata**: titles/descriptions/tags with [placeholders](/docs/en/reference/placeholders.md).
- **Monitoring**: CPU, RAM, FPS, bitrate – live per stream.
- **Recording & replay**, **preflight checks**, **notifications**, **scheduler**, **backup/restore**.

## What CastCore is *not*

CastCore is not a simple "FFmpeg web wrapper". It is an **operations suite**: manage
sources, analyse media, plan streams, control FFmpeg safely, explain failures in plain
language and simplify operations.

## Next steps

- [Install with Docker Compose](/docs/en/getting-started/installation-docker.md)
- [Setup wizard](/docs/en/getting-started/first-setup.md)
- [Quickstart: your first stream](/docs/en/getting-started/quickstart.md)

## Related pages

- [Architecture](/docs/en/developer-guide/architecture.md)
- [Glossary](/docs/en/reference/glossary.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

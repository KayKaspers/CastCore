---
title: "MediaMTX integration"
description: "Attach the optional media router (RTMP/SRT/WebRTC) and monitor ingest live."
lang: en
audience: "Administrators"
status: stable
lastReviewed: 2026-06-25
---

# MediaMTX integration

> **MediaMTX** is an optional media router that accepts and forwards common protocols
> (RTSP, RTMP, SRT, WebRTC, HLS). CastCore stays the **control plane** and reads ingest
> status read-only via the MediaMTX API.

**Audience:** administrators.

## Role split

- **MediaMTX**: accepts incoming streams and routes/proxies protocols.
- **FFmpeg** (via CastCore): transcodes and distributes to destinations.
- **CastCore**: control, monitoring, configuration.

## Enable

1. In `.env`:
   ```ini
   MEDIAMTX_ENABLED=true
   MEDIAMTX_API_URL=http://mediamtx:9997
   ```
2. Start the service via its compose profile:
   ```bash
   docker compose --profile mediamtx up -d
   ```
3. In **Monitoring** (`/monitoring`) the **Ingest (MediaMTX)** panel appears with
   reachability and active ingest paths.

## Ingest status

For each path the panel shows: **status** (live/ready), **source** (e.g. `rtmpConn`,
`srtConn`), **tracks**, **received bytes** and **reader count**. With no active publishers
the list is empty – that is normal.

## Ports

| Protocol | Default port |
| --- | --- |
| RTMP | 1935 |
| RTSP | 8554 |
| SRT | 8890/UDP |
| WebRTC | 8889 (HTTP), 8189/UDP (ICE) |
| HLS | 8888 |
| API | 9997 (internal only) |

Publish only the protocol ports you actually need on the host or reverse proxy.

## Security

> 🔐 MediaMTX's **API/metrics ports** are reachable only on the internal `castcore` Docker
> network and are **not** published to the host – only the control plane queries them. If
> you expose MediaMTX beyond the host, configure real users/passwords in
> `deploy/mediamtx/mediamtx.yml` (the `authInternalUsers` section) and restrict
> `publish`/`read` accordingly.

## Troubleshooting

- **Panel shows "Unreachable"**: is the container running
  (`docker compose --profile mediamtx ps`)? Is `MEDIAMTX_API_URL` correct? Are both services
  on the same `castcore` network?
- **401 from the API**: the API user needs the `api`/`metrics` actions in
  `authInternalUsers` (already set in the shipped config).

## Related pages

- [Monitoring](/docs/en/user-guide/monitoring.md)
- [Deployment](/docs/en/admin-guide/deployment.md)
- [Environment variables](/docs/en/reference/environment-variables.md)

---
_Last reviewed: 2026-06-25 · Status: stable_

---
title: "Glossary"
description: "Bilingual glossary of streaming terms."
lang: en
audience: "All roles"
status: stable
lastReviewed: 2026-06-24
---

# Glossary

> Short definitions of the key terms in CastCore. German edition:
> [`/docs/de/reference/glossary.md`](/docs/de/reference/glossary.md).

| Term | Meaning |
| --- | --- |
| **FFmpeg** | Tool to record, convert and stream audio/video. |
| **ffprobe** | Analyses media files (codec, resolution, duration, bitrate). |
| **RTMP** | Real-Time Messaging Protocol – common ingest protocol (Twitch, YouTube). |
| **RTSP** | Streaming protocol, common for IP cameras. |
| **HLS** | HTTP Live Streaming – segmented streaming over HTTP (`.m3u8` + `.ts`). |
| **LL-HLS** | Low-latency HLS. |
| **SRT** | Secure Reliable Transport – low-loss transport protocol. |
| **WebRTC** | Real-time browser communication, very low latency. |
| **Transcoding** | Re-encoding audio/video (change codec/bitrate/resolution). |
| **Remuxing** | Repackaging into another container without re-encoding. |
| **Bitrate** | Data rate per second (e.g. 6000 kbit/s). |
| **Framerate** | Frames per second (FPS). |
| **GOP / keyframe** | Group of pictures / full frame; affects segmentation/latency. |
| **Codec** | Encoding method (e.g. H.264/libx264, AAC). |
| **Container / muxer** | File format bundling streams (MP4, MPEG-TS). |
| **Preset / tune** | x264 speed/quality profile and fine-tuning. |
| **Stream copy** | Pass-through without re-encoding (`-c copy`). |
| **Input / output / destination** | Source / output / concrete target (URL+key). |
| **Platform** | Target platform (Twitch, YouTube, Kick, own RTMP …). |
| **Storage source / mount** | Source (local/SMB/NFS/cloud) and how it is attached. |
| **SMB / NFS / WebDAV / rclone** | Protocols/tools for network and cloud storage. |
| **OAuth** | Authorization method for platform accounts. |
| **Stream key** | Secret key to publish to a platform. |
| **Preflight check** | Readiness check before stream start (🟢/🟡/🔴). |
| **Health score** | Stream health rating from live metrics. |
| **Channel** | Linear 24/7 channel from a playlist. |
| **Playlist** | Ordered/shuffled list of media. |
| **EPG / XMLTV** | Electronic program guide and its XML format. |
| **M3U** | Playlist/lineup format for IPTV players. |

## Related pages

- [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)
- [What is CastCore?](/docs/en/getting-started/overview.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

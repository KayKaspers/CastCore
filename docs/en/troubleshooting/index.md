---
title: "Troubleshooting"
description: "Entry point to troubleshooting by symptom."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-24
---

# Troubleshooting

> Find your symptom and follow the link. Each page follows **Symptom → Possible causes →
> Diagnosis → Fix → Relevant logs**.

## By symptom

| Symptom | Page |
| --- | --- |
| FFmpeg won't start / not found | [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md) |
| Stream won't start | [Stream not starting](/docs/en/troubleshooting/stream-not-starting.md) |
| No video / no audio / RTMP rejected / wrong stream key | [Platform errors](/docs/en/troubleshooting/platform-errors.md) |
| SMB mount fails | [SMB problems](/docs/en/troubleshooting/smb-problems.md) |
| Encoding speed < 1.0x, high CPU | [Performance](/docs/en/troubleshooting/performance.md) |
| Containers won't start, DB/Redis unreachable | [Docker problems](/docs/en/troubleshooting/docker.md) |
| Native installation issues | [Native installation](/docs/en/troubleshooting/native-installation.md) |

## General first diagnosis

1. Open the **live logs** of the affected stream job – CastCore also shows plain-language
   hints (stream health assistant).
2. Run the **preflight check** – it verifies source, video/audio, output URL, stream key,
   disk space.
3. Inspect the **service logs**:
   ```bash
   docker compose logs -f backend process-manager
   ```

## Related pages

- [Logs](/docs/en/admin-guide/logs.md)
- [Monitoring](/docs/en/user-guide/monitoring.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

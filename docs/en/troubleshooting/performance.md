---
title: "Performance"
description: "Encoding speed < 1.0x, high CPU, bottlenecks."
lang: en
audience: "Operators / Administrators"
status: stable
lastReviewed: 2026-06-26
---

# Performance

> When the machine can't keep real time or the load is too high.

**Audience:** operators / administrators.

## Symptom: encoding speed < 1.0×

**Meaning:** FFmpeg encodes slower than real time → the stream stutters/falls behind.
**Possible causes:** resolution/bitrate too high, preset too slow, CPU overloaded, several
parallel streams.
**Fix:**

- In the [FFmpeg profile](/docs/en/reference/ffmpeg-profiles.md) choose a **faster preset**
  (e.g. `veryfast`/`ultrafast`) and/or **lower resolution/bitrate**.
- Use a **GPU encoder** (NVENC/QSV/VAAPI) if hardware is available.
- Reduce the number of parallel streams.

## Symptom: high CPU load

**Diagnosis:** [Monitoring](/docs/en/user-guide/monitoring.md) – CPU per output and total.
**Fix:** as above; use stream copy where possible (no re-encode).

## Check in advance

Use the [dry-run](/docs/en/user-guide/preflight-checks.md) to estimate encoding speed
**before** going live.

## Health score 🔴 red / 🟡 yellow

The **stream health score** (dashboard) summarizes the live metrics. Click a job to see the
reasons:

- **Encoding speed critical/low** → check CPU load/profile (see above).
- **Reconnects / output crashed** → check network/destination, review logs
  ([Stream not starting](/docs/en/troubleshooting/stream-not-starting.md)).
- **No throughput** → FFmpeg emits no FPS/bitrate – check the input/source.
- **Unknown (gray)** → the job is not running; the score appears once it is live.

## Relevant values

- **speed** (×), **fps**, **CPU%**, **RAM** per output in monitoring.
- Dropped frames, where available.

## Related pages

- [Monitoring](/docs/en/user-guide/monitoring.md)
- [FFmpeg profiles](/docs/en/reference/ffmpeg-profiles.md)
- [System requirements](/docs/en/admin-guide/system-requirements.md)

---
_Last reviewed: 2026-06-26 · Status: stable_

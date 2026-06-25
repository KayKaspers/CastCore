---
title: "Preflight checks"
description: "Check before start whether a job is ready (traffic light)."
lang: en
audience: "Users / Operators"
status: stable
lastReviewed: 2026-06-24
---

# Preflight checks

> The preflight check verifies **before** stream start whether a job is ready and returns
> a traffic-light result.

**Audience:** users / operators. Invoke: **Stream jobs → Preflight**.

## Result traffic light

- 🟢 **Green** – ready to start.
- 🟡 **Yellow** – warnings (e.g. no audio), start possible.
- 🔴 **Red** – blocking errors, start not advisable.

## Checked items (selection)

| Check | Meaning |
| --- | --- |
| **source_readable** | Source is readable with ffprobe. |
| **has_video / has_audio** | Input contains a video / audio track. |
| **outputs / destination** | At least one active output with a destination. |
| **output_url / stream_key** | Output URL set, stream key present. |
| **disk_space** | Enough free space for recordings. |

## Step by step

1. Click **Preflight** on a job.
2. Fix red items first (source, output, stream key, disk space).
3. **Start** when green/yellow.

## Dry-run / test stream

Besides preflight there is the **dry-run**: a short test encode (~5 seconds) using the
job's profile – **without** a live output and **without** contacting the real destination.

- Invoke: **Stream jobs → Dry-run**.
- Result: 🟢 ok / 🔴 failed, measured **encoding speed** and **FPS**, a plain-language
  message and the last log lines.
- Purpose: checks that the source decodes and the profile encodes, and estimates load.

> ⚠️ **Speed < 1.0×** in the dry-run means the machine can't keep real time →
> [Performance](/docs/en/troubleshooting/performance.md).

## Notes

> 💡 Preflight uses **ffprobe** on the first source – network/mount sources must be
> reachable for this.

## Related pages

- [Stream jobs](/docs/en/user-guide/streams.md)
- [Stream not starting](/docs/en/troubleshooting/stream-not-starting.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

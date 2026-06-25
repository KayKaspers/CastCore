---
title: "Setup wizard (first run)"
description: "Walk through the setup wizard: language, admin, system check."
lang: en
audience: "Beginners"
status: stable
lastReviewed: 2026-06-24
---

# Setup wizard (first run)

> On first launch CastCore detects that no administrator exists yet and shows the
> create-admin form directly.

**Audience:** beginners.
**Requirements:** a running CastCore instance ([Docker](/docs/en/getting-started/installation-docker.md)
or [native](/docs/en/getting-started/installation-native.md)).

## Steps

1. **Open `https://<DOMAIN>`.** Accept the certificate warning for `localhost`.
2. **Create the admin** (first run): username + password (min. 8 chars), language (DE/EN).
   You are signed in automatically afterwards.
3. **Run the system check** (Settings → Setup): verifies FFmpeg/ffprobe, write access to
   the data directories and free disk space. Result as a traffic light 🟢/🟡/🔴.
4. **Finish the steps** and mark setup as complete.

## Wizard steps at a glance

Language · admin user · deployment detection · FFmpeg path · ffprobe path · data dir ·
media dir · log dir · storage concept · system check · completion.

## Notes

> 💡 Only **one** admin can be created via first-run. If a user already exists, first-run
> is blocked (HTTP 409) – sign in instead.

> 🔐 Add more users and roles later under [Users & roles](/docs/en/user-guide/users-roles.md).

## If something fails

- Login fails → [Troubleshooting](/docs/en/troubleshooting/index.md)
- FFmpeg not found → [FFmpeg errors](/docs/en/troubleshooting/ffmpeg-errors.md)

## Related pages

- [Quickstart: your first stream](/docs/en/getting-started/quickstart.md)
- [Roles](/docs/en/reference/roles.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

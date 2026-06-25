# CastCore — Roadmap

Four phases. Each builds on a working, deployable previous phase. ✅ = scaffolded in
this repo, ▢ = planned.

## Phase 1 — Solid base (MVP, deployable) — ✅ COMPLETE
- ✅ Docker-compose installation & project skeleton
- ✅ DE/EN i18n foundation (frontend `de.json`/`en.json`, backend error codes)
- ✅ Setup Wizard (language, admin user, deployment detect, FFmpeg/ffprobe check, dirs, storage)
- ✅ Auth: login, JWT refresh+rotation, roles (Admin/Operator/Viewer)
- ✅ Stream jobs: create/start/stop/restart, live logs (WS)
- ✅ Local sources + SMB sources (test/mount/browse, encrypted creds)
- ✅ FFmpeg profiles + **Command Builder** (safe argv, masked preview, tested)
- ✅ Destinations (encrypted stream keys) + preflight check
- ✅ Dashboard
- ✅ Backup/Restore (basic, logical gz-JSON)

## Phase 2 — Streaming suite — ✅ mostly complete
- ✅ Media library + ffprobe analysis
- ✅ Playlists (sequential/shuffle/loop, resolve)
- ✅ Scheduler (once/interval/daily; start/stop/backup/scan)
- ✅ Preflight checks (delivered in Phase 1)
- ✅ Dry-run / teststream (short test encode + speed/fps report)
- ✅ Recording + replay (per-job, retention field)
- ▢ Internal HLS preview / webplayer
- ✅ Platform metadata API + template resolution (+ secure thumbnail/asset management)
- ✅ Notifications (email/webhook/discord/telegram/gotify/slack)
- ✅ Richer monitoring views (system + per-output live metrics)
- ✅ Status reconciliation (PM→DB) + background loops (status consumer, scheduler)

## Phase 3 — Broadcast / channel features
- ▢ 24/7 linear channels + channel scheduler
- ▢ EPG / XMLTV export
- ▢ M3U export
- ▢ Fallback content, repeats, media rotation
- ▢ Auto-rescan
- ▢ Jellyfin / Plex / Emby integration prep

## Phase 4 — Advanced / pro
- ▢ MediaMTX integration
- ▢ WebRTC / LL-HLS, latency profiles
- ▢ GPU encoding profiles (NVENC/QSV/VAAPI)
- ▢ Cluster / multi-worker model
- ▢ Prometheus / Grafana
- ▢ Multi-tenancy
- ▢ Webhook / API automation, plugin system
- ▢ Platform OAuth
- ▢ Audit / compliance mode, optional 2FA

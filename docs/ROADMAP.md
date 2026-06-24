# CastCore — Roadmap

Four phases. Each builds on a working, deployable previous phase. ✅ = scaffolded in
this repo, ▢ = planned.

## Phase 1 — Solid base (MVP, deployable)
- ✅ Docker-compose installation & project skeleton
- ✅ DE/EN i18n foundation (frontend `de.json`/`en.json`, backend error codes)
- ▢ Setup Wizard (language, admin user, deployment detect, FFmpeg/ffprobe check, dirs, storage)
- ▢ Auth: login, JWT, roles (Admin/Operator/Viewer)
- ▢ Stream jobs: create/edit/start/stop/restart, live logs (WS)
- ▢ Local sources + SMB sources
- ▢ FFmpeg profiles + **Command Builder** (safe argv, preview, tested)
- ▢ Platform profiles: title/description/thumbnail
- ▢ Dashboard
- ▢ Backup/Restore (basic)

## Phase 2 — Streaming suite
- ▢ Media library + ffprobe analysis
- ▢ Playlists
- ▢ Scheduler
- ▢ Preflight checks
- ▢ Dry-run / teststream
- ▢ Recording
- ▢ Internal HLS preview / webplayer
- ▢ Platform metadata API + template resolution
- ▢ Notifications (email/webhook/discord/telegram/gotify)
- ▢ Richer monitoring views

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

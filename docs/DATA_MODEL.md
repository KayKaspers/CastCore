# CastCore — Data Model

PostgreSQL via SQLAlchemy 2.0 (async) + Alembic migrations. All tables carry
`id` (UUID), `created_at`, `updated_at`. Secrets columns are encrypted at rest
(Fernet) and never serialized in clear. `→` denotes a foreign key.

## Security & users

| Table | Key fields |
| --- | --- |
| `users` | username, email, password_hash (argon2), language(de/en), is_active, totp_secret(enc, nullable), last_login_at |
| `roles` | name(admin/operator/viewer), permissions(jsonb) |
| `user_roles` | user→users, role→roles |
| `sessions` | user→users, refresh_token_hash, user_agent, ip, expires_at, revoked_at |
| `api_tokens` | user→users, name, token_hash, scopes(jsonb), last_used_at, expires_at |
| `audit_events` | actor→users(nullable), action, target_type, target_id, ip, meta(jsonb), at |

## Settings & setup

| Table | Key fields |
| --- | --- |
| `settings` | key, value(jsonb), scope(global/user), user→users(nullable) |
| `setup_state` | step, status(pending/done/skipped), data(jsonb), completed_at |

## Streaming

| Table | Key fields |
| --- | --- |
| `stream_jobs` | name, type(single/channel), status, source→storage_sources(nullable), stream_profile→stream_profiles, autostart, schedule(jsonb), fallback_policy(jsonb), enabled |
| `stream_profiles` | name, ffmpeg_profile→ffmpeg_profiles, latency_profile(standard/low/ull), recording_enabled, recording_config(jsonb) |
| `ffmpeg_profiles` | name, global_opts(jsonb), video(jsonb: codec/res/fps/bitrate/preset/tune/gop/pix_fmt), audio(jsonb), filters(jsonb), copy_mode(bool), expert_args(jsonb) |
| `inputs` | stream_job→stream_jobs, kind(file/url/device), uri, input_opts(jsonb), loop, reconnect(jsonb), order |
| `outputs` | stream_job→stream_jobs, destination→destinations, format(hls/rtmp/srt), output_opts(jsonb), enabled |
| `destinations` | name, platform→platforms(nullable), url, stream_key(enc), bitrate_override, profile_override(jsonb), enabled, kind(platform/rtmp/hls/recording/preview) |
| `process_status` | output→outputs, pid, state(starting/running/reconnecting/stopped/failed), started_at, fps, bitrate_kbps, speed, dropped_frames, reconnect_count, cpu_pct, rss_mb, updated_at |
| `health_checks` | stream_job→stream_jobs, score(0-100), level(green/yellow/red), signals(jsonb), at |
| `preflight_reports` | stream_job→stream_jobs, level(green/yellow/red), checks(jsonb), created_at |

## Platforms & metadata

| Table | Key fields |
| --- | --- |
| `platforms` | type(twitch/youtube/kick/facebook/rtmp/custom), name, capabilities(jsonb) |
| `platform_accounts` | platform→platforms, label, oauth_refresh_token(enc, nullable), api_key(enc, nullable), status, last_checked_at |
| `platform_profiles` | platform_account→platform_accounts, name, ingest_url, default_metadata(jsonb) |
| `platform_metadata` | scope(platform/stream), platform_profile→platform_profiles(nullable), stream_job→stream_jobs(nullable), title, description_template, category, tags(jsonb), language, visibility, thumbnail→thumbnails(nullable), scheduled_start |
| `thumbnails` | filename(safe), path, width, height, mime, size_bytes, platform_hint, sha256 |
| `assets` | filename(safe), path, kind(image/video/audio), mime, size_bytes, used(bool) |

## Sources & storage

| Table | Key fields |
| --- | --- |
| `storage_sources` | name, class(local/network/cloud), type(file/folder/watch/smb/nfs/sftp/ftp/webdav/http/rtsp/rtmp/hls/srt/gdrive/dropbox/onedrive/s3/nextcloud/b2/r2/rclone), config(jsonb), read_only, automount, status(online/offline/error), last_scan_at |
| `smb_sources` | storage_source→storage_sources, server, share, domain, username, password(enc), smb_version, mount_path |
| `nfs_sources` | storage_source→storage_sources, server, export, mount_path, options |
| `cloud_sources` | storage_source→storage_sources, provider, rclone_remote, oauth(enc, nullable), api_secret(enc, nullable), cache_dir, mode(sync/mount) |
| `mounts` | storage_source→storage_sources, mount_path, state(mounted/unmounted/error), last_error, mounted_at |
| `media_library_items` | storage_source→storage_sources, rel_path, filename, kind, size_bytes, mtime, streamable(bool), problem_flags(jsonb), thumbnail→thumbnails(nullable) |
| `media_probe_data` | media_item→media_library_items, container, duration_s, video_codec, audio_codec, width, height, fps, video_bitrate, audio_bitrate, raw_ffprobe(jsonb), probed_at |

## Channels & playlists

| Table | Key fields |
| --- | --- |
| `channels` | name, logo→assets(nullable), description, source→storage_sources(nullable), playlist→playlists(nullable), stream_profile→stream_profiles, fallback_asset→assets(nullable), epg_enabled, recording_enabled, outputs(jsonb) |
| `channel_schedule` | channel→channels, rules(jsonb: repeat/shuffle/order), timezone |
| `channel_programs` | channel→channels, media_item→media_library_items(nullable), playlist_item→playlist_items(nullable), start_at, end_at, title, is_fallback |
| `playlists` | name, mode(sequential/shuffle/loop), description |
| `playlist_items` | playlist→playlists, media_item→media_library_items, order, enabled |

## Recording, ops & system

| Table | Key fields |
| --- | --- |
| `recordings` | stream_job→stream_jobs(nullable), channel→channels(nullable), path, filename_template, segment_config(jsonb), state, started_at, ended_at, size_bytes, retention_until |
| `replay_items` | recording→recordings, title, in_point_s, out_point_s, highlight(bool), vod_ready |
| `scheduler_entries` | kind(stream/channel/backup/scan), target_id, cron, next_run_at, enabled, last_run_at, last_status |
| `notifications` | channel(email/webhook/discord/telegram/gotify/slack), config(jsonb, secrets enc), events(jsonb), enabled |
| `backups` | path, kind(manual/scheduled), encrypted, size_bytes, includes(jsonb), created_at, status |
| `update_state` | current_version, available_version, channel(stable/beta), last_checked_at, migration_status |
| `logs` | source(backend/process_manager/worker/ffmpeg), level, stream_job→stream_jobs(nullable), message, meta(jsonb), at |

## Relationship notes

- A **stream_job** has many **inputs** and many **outputs**; each **output** targets a
  **destination**; a destination may map to a **platform** (metadata) or be a raw
  rtmp/hls/recording/preview sink.
- **process_status** is per **output** (one supervised FFmpeg process per active
  output for multi-destination; single process for stream-copy fan-out where possible).
- **storage_sources** is the polymorphic root; `smb/nfs/cloud_sources` hold type detail.
- **channels** reuse stream_profiles + outputs; **channel_programs** materialise the
  schedule for EPG/XMLTV and M3U export.

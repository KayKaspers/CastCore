# CastCore — API

- **Base:** `/api/v1`
- **Transport:** REST (JSON) for CRUD; **WebSocket** (`/api/v1/ws/...`) and **SSE** for
  live logs and status streams.
- **Auth:** `Authorization: Bearer <access_jwt>`; refresh via `/auth/refresh`.
  API tokens for automation via `X-API-Key`.
- **Errors:** machine-readable **translatable codes**, not English prose:
  ```json
  { "error": { "code": "preflight.source_unreachable",
                "params": { "source": "Studio NAS" },
                "level": "error" } }
  ```
  The frontend maps `code` → localized string via i18next.

## REST surface (representative)

| Group | Endpoints |
| --- | --- |
| Auth | `POST /auth/login` · `POST /auth/refresh` · `POST /auth/logout` · `GET /auth/me` · `POST /auth/2fa/verify` |
| Setup | `GET /setup/state` · `POST /setup/step/{step}` · `POST /setup/syscheck` · `POST /setup/complete` |
| Users | `GET/POST /users` · `GET/PATCH/DELETE /users/{id}` · `GET /roles` |
| Settings | `GET/PATCH /settings` · `GET/PATCH /settings/me` |
| Stream jobs | `GET/POST /stream-jobs` · `GET/PATCH/DELETE /stream-jobs/{id}` · `POST /stream-jobs/{id}/duplicate` |
| Process control | `POST /stream-jobs/{id}/start` · `/stop` · `/restart` · `/pause` |
| FFmpeg profiles | `GET/POST /ffmpeg-profiles` · `GET/PATCH/DELETE /ffmpeg-profiles/{id}` |
| Command preview | `POST /ffmpeg/preview` → masked argv + warnings |
| Preflight | `POST /stream-jobs/{id}/preflight` → report (green/yellow/red) |
| Dry-run | `POST /stream-jobs/{id}/dry-run` → test-encode report |
| Channels | `GET/POST /channels` · `GET/PATCH/DELETE /channels/{id}` · `GET /channels/{id}/epg.xml` · `GET /channels/{id}/playlist.m3u` |
| Playlists | `GET/POST /playlists` · `GET/PATCH/DELETE /playlists/{id}` · `POST /playlists/{id}/items` |
| Storage sources | `GET/POST /storage-sources` · `GET/PATCH/DELETE /storage-sources/{id}` · `POST /storage-sources/{id}/test` · `POST /storage-sources/{id}/scan` |
| Mounts | `POST /mounts/{source_id}/mount` · `/unmount` · `GET /mounts/{source_id}/status` |
| Media library | `GET /media` · `GET /media/{id}` · `POST /media/{id}/probe` · `GET /media/{id}/thumbnail` |
| Platforms | `GET/POST /platforms` · `POST /platform-accounts/{id}/test` · OAuth `GET /platforms/{type}/oauth/start` · `GET /platforms/{type}/oauth/callback` |
| Platform metadata | `GET/PUT /stream-jobs/{id}/metadata/{platform}` · `POST /metadata/resolve` (apply templates) |
| Thumbnails/Assets | `POST /assets` (upload, validated) · `GET /assets` · `DELETE /assets/{id}` |
| Recording | `GET /recordings` · `POST /stream-jobs/{id}/recording` (toggle) · `GET/DELETE /recordings/{id}` |
| Replay | `GET /replay` · `POST /replay` · `PATCH /replay/{id}` |
| Scheduler | `GET/POST /scheduler` · `GET/PATCH/DELETE /scheduler/{id}` |
| Notifications | `GET/POST /notifications` · `POST /notifications/{id}/test` |
| Monitoring | `GET /system/health` · `GET /system/metrics` · `GET /stream-jobs/{id}/status` |
| Backup/Restore | `POST /backups` · `GET /backups` · `GET /backups/{id}/download` · `POST /backups/{id}/restore` |
| Update | `GET /update/state` · `POST /update/check` · `POST /update/migrate` |
| Audit | `GET /audit` |

## Live channels (WebSocket / SSE)

| Channel | Payload |
| --- | --- |
| `WS /api/v1/ws/logs/{stream_job_id}` | parsed FFmpeg log lines + plain-language hints |
| `WS /api/v1/ws/status` | per-job state, fps, bitrate, speed, health score, reconnects |
| `WS /api/v1/ws/system` | CPU/RAM/disk/network/process counts |
| `SSE /api/v1/sse/preflight/{id}` | streamed preflight check progress |

Backend subscribes to Redis pub/sub channels populated by the Process Manager and fans
out to connected clients; control commands flow back over Redis.

## Conventions

- Pagination: `?limit=&offset=`, responses `{ items, total, limit, offset }`.
- Secrets (`stream_key`, passwords, tokens) are **write-only**: accepted on
  create/update, returned masked (`••••1234`) and never in logs.
- All list/detail endpoints respect RBAC (Admin/Operator/Viewer) — see SECURITY.md.

// API entity shapes (mirrors backend Pydantic schemas).

export interface SystemHealth {
  status: string;
  version: string;
  environment: string;
  ffmpeg_available: boolean;
  ffprobe_available: boolean;
}

export interface StepState {
  step: string;
  status: "pending" | "done" | "skipped";
}

export interface SetupStatus {
  completed: boolean;
  current_step: string | null;
  steps: StepState[];
}

export interface SystemCheckItem {
  key: string;
  ok: boolean;
  detail: string | null;
}

export interface SystemCheckResult {
  level: "green" | "yellow" | "red";
  items: SystemCheckItem[];
}

export interface FFmpegProfile {
  id: string;
  name: string;
  copy_mode: boolean;
  video: Record<string, unknown>;
  audio: Record<string, unknown>;
  filters?: Record<string, unknown>;
  expert_args?: string[];
  global_opts?: Record<string, unknown>;
}

export interface Destination {
  id: string;
  name: string;
  kind: string;
  url: string;
  enabled: boolean;
  has_stream_key: boolean;
}

export interface StreamJob {
  id: string;
  name: string;
  type: string;
  status: string;
  autostart: boolean;
  enabled: boolean;
  ffmpeg_profile_id: string | null;
  created_at: string;
}

export interface CommandPreview {
  previews: Record<string, string>;
}

export interface PreflightCheck {
  key: string;
  level: "ok" | "warn" | "error";
  detail: string | null;
}

export interface PreflightReport {
  level: "green" | "yellow" | "red";
  checks: PreflightCheck[];
}

export interface DryRunReport {
  ok: boolean;
  returncode?: number;
  speed: number | null;
  fps: number | null;
  message: string;
  log_tail: string[];
}

export interface StorageSource {
  id: string;
  name: string;
  source_class: string;
  type: string;
  path: string | null;
  effective_path: string | null;
  read_only: boolean;
  automount: boolean;
  status: string;
  last_error: string | null;
  smb: {
    server: string;
    share: string;
    mount_path: string;
    has_password: boolean;
  } | null;
}

export interface BrowseEntry {
  name: string;
  rel_path: string;
  abs_path: string;
  is_dir: boolean;
  size: number;
  streamable: boolean;
}

export interface BrowseResult {
  base: string;
  subpath: string;
  entries: BrowseEntry[];
}

export interface TestResult {
  ok: boolean;
  detail: string | null;
}

export interface MediaProbe {
  container: string | null;
  duration_s: number | null;
  video_codec: string | null;
  audio_codec: string | null;
  width: number | null;
  height: number | null;
  fps: number | null;
}

export interface MediaItem {
  id: string;
  storage_source_id: string;
  rel_path: string;
  filename: string;
  kind: string;
  size_bytes: number;
  streamable: boolean;
  problem_flags: Record<string, unknown>;
  probe: MediaProbe | null;
}

export interface ScanResult {
  files: number;
  indexed: number;
  probed: number;
}

export interface SystemMetrics {
  cpu_percent: number;
  mem_percent: number;
  mem_used_mb: number;
  mem_total_mb: number;
  disk_percent: number;
  disk_free_gb: number;
  ffmpeg_processes: number;
}

export interface OutputMetrics {
  output_id: string;
  job_id: string;
  job_name: string;
  destination: string | null;
  state: string;
  fps: number | null;
  bitrate_kbps: number | null;
  speed: number | null;
  cpu_pct: number | null;
  rss_mb: number | null;
  reconnect_count: number;
  started_at: string | null;
}

export interface Channel {
  id: string;
  name: string;
  description: string | null;
  playlist_id: string | null;
  ffmpeg_profile_id: string | null;
  fallback_uri: string | null;
  hls_enabled: boolean;
  epg_enabled: boolean;
  enabled: boolean;
  status: string;
}

export interface PlaylistItem {
  id: string;
  media_item_id: string;
  filename: string;
  duration_s: number | null;
  order: number;
  enabled: boolean;
}

export interface Playlist {
  id: string;
  name: string;
  mode: string;
  description: string | null;
  item_count: number;
  items?: PlaylistItem[];
}

export interface SchedulerEntry {
  id: string;
  name: string;
  action: string;
  target_id: string | null;
  schedule_type: string;
  run_at: string | null;
  interval_minutes: number;
  daily_time: string | null;
  enabled: boolean;
  next_run_at: string | null;
  last_run_at: string | null;
  last_status: string | null;
}

export interface Recording {
  id: string;
  stream_job_id: string | null;
  filename: string;
  state: string;
  size_bytes: number;
  duration_s: number | null;
  started_at: string | null;
  ended_at: string | null;
  retention_until: string | null;
}

export interface Asset {
  id: string;
  filename: string;
  original_name: string | null;
  kind: string;
  mime: string;
  size_bytes: number;
  width: number | null;
  height: number | null;
  used: boolean;
}

export interface ManagedUser {
  id: string;
  username: string;
  email: string | null;
  language: string;
  is_active: boolean;
  roles: string[];
  totp_enabled: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface ApiToken {
  id: string;
  name: string;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface ApiTokenCreated extends ApiToken {
  token: string;
}

export interface AuthSession {
  id: string;
  user_agent: string | null;
  ip: string | null;
  created_at: string;
  expires_at: string;
  current: boolean;
}

export interface AuditEvent {
  id: string;
  actor: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  ip: string | null;
  meta: Record<string, unknown>;
  at: string;
}

export interface NotificationChannel {
  id: string;
  name: string;
  channel: string;
  events: string[];
  config: Record<string, unknown>;
  enabled: boolean;
  has_secret: boolean;
}

export interface Backup {
  id: string;
  filename: string;
  kind: string;
  size_bytes: number;
  status: string;
  created_at: string;
}

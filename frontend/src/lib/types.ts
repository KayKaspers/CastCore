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

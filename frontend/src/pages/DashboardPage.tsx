import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Panel } from "../components/ui";
import { api } from "../lib/api";
import type { StreamJob, SystemHealth } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function DashboardPage() {
  const { t } = useTranslation();
  const health = useAsync<SystemHealth>(() => api.get("/system/health"), []);
  const jobs = useAsync<StreamJob[]>(() => api.get("/stream-jobs"), []);

  const running = (jobs.data ?? []).filter((j) => j.status === "running" || j.status === "starting").length;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-mist">{t("nav.dashboard")}</h1>
        <p className="text-slate text-sm">{t("app.tagline")}</p>
      </header>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label={t("nav.streamJobs")} value={String(jobs.data?.length ?? "…")} />
        <Stat label="Live" value={String(running)} accent />
        <Stat label="FFmpeg" value={health.data?.ffmpeg_available ? "✓" : "✗"} />
        <Stat label="Version" value={health.data?.version ?? "…"} />
      </div>

      <Panel>
        <h2 className="text-mist mb-3">{t("common.status")}</h2>
        {health.error && <p className="text-danger text-sm">{health.error}</p>}
        {health.data && (
          <div className="space-y-2 text-sm">
            <Row label="Environment" value={health.data.environment} />
            <Row label="ffmpeg" value={<Badge status={health.data.ffmpeg_available ? "green" : "red"} />} />
            <Row label="ffprobe" value={<Badge status={health.data.ffprobe_available ? "green" : "red"} />} />
          </div>
        )}
      </Panel>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <Panel className="!p-4">
      <div className="text-xs uppercase tracking-wide text-slate">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${accent ? "text-core-green" : "text-mist"}`}>{value}</div>
    </Panel>
  );
}

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-slate/10 pb-2">
      <span className="text-slate">{label}</span>
      <span className="text-mist">{value}</span>
    </div>
  );
}

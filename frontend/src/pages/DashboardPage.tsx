import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";

import HelpLink from "../components/HelpLink";
import { Badge, Panel } from "../components/ui";
import { api } from "../lib/api";
import type { JobHealth, JobHealthSummary, StreamJob, SystemHealth } from "../lib/types";
import { useAsync } from "../lib/useAsync";

const HEALTH_BADGE: Record<string, string> = { green: "running", yellow: "yellow", red: "failed", gray: "stopped" };

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

      <StreamHealth />

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

function StreamHealth() {
  const { t } = useTranslation();
  const list = useAsync<JobHealthSummary[]>(() => api.get("/monitoring/health"), []);
  const [open, setOpen] = useState<string | null>(null);
  const [detail, setDetail] = useState<JobHealth | null>(null);

  useEffect(() => {
    const id = setInterval(() => list.reload(), 4000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggle = async (jobId: string) => {
    if (open === jobId) { setOpen(null); setDetail(null); return; }
    setOpen(jobId); setDetail(null);
    try { setDetail(await api.get<JobHealth>(`/monitoring/jobs/${jobId}/health`)); } catch { /* ignore */ }
  };

  return (
    <Panel className="space-y-2">
      <h2 className="text-mist mb-1 flex items-center gap-2">
        {t("health.title")} <HelpLink page="user-guide/monitoring.md" />
      </h2>
      {(list.data?.length ?? 0) === 0 && <p className="text-xs text-slate">{t("health.noJobs")}</p>}
      <ul className="space-y-1">
        {(list.data ?? []).map((j) => (
          <li key={j.job_id} className="border-b border-slate/10 pb-1">
            <button className="w-full flex items-center justify-between text-left" onClick={() => toggle(j.job_id)}>
              <span className="text-mist text-sm">{j.name}</span>
              <span className="flex items-center gap-2">
                <span className="text-slate text-xs">{j.score == null ? "—" : `${j.score}/100`}</span>
                <Badge status={HEALTH_BADGE[j.status] ?? "stopped"}>{t(`health.status.${j.status}`)}</Badge>
              </span>
            </button>
            {open === j.job_id && detail && (
              <ul className="mt-1 ml-2 space-y-0.5">
                {detail.reasons.map((r, i) => (
                  <li key={i} className="text-xs flex items-start gap-2">
                    <span className={r.level === "ok" ? "text-core-green" : r.level === "warn" ? "text-warning" : r.level === "error" ? "text-danger" : "text-slate"}>
                      {r.level === "ok" ? "✓" : r.level === "info" ? "•" : "!"}
                    </span>
                    <span className="text-slate">{t(`health.reason.${r.code}`, r.params)}</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </Panel>
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

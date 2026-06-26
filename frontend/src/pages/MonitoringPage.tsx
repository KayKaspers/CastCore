import { useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Panel } from "../components/ui";
import { api } from "../lib/api";
import type { MediamtxStatus, OutputMetrics, SystemMetrics } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function MonitoringPage() {
  const { t } = useTranslation();
  const sys = useAsync<SystemMetrics>(() => api.get("/monitoring/system"), []);
  const outputs = useAsync<OutputMetrics[]>(() => api.get("/monitoring/outputs"), []);
  const mtx = useAsync<MediamtxStatus>(() => api.get("/mediamtx/status"), []);

  // Auto-refresh every 2s.
  useEffect(() => {
    const id = setInterval(() => { sys.reload(); outputs.reload(); mtx.reload(); }, 2000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const s = sys.data;
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.monitoring")}</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Gauge label="CPU" value={s ? `${s.cpu_percent.toFixed(0)}%` : "…"} pct={s?.cpu_percent} />
        <Gauge label="RAM" value={s ? `${s.mem_percent.toFixed(0)}%` : "…"} pct={s?.mem_percent}
               sub={s ? `${(s.mem_used_mb / 1024).toFixed(1)}/${(s.mem_total_mb / 1024).toFixed(1)} GB` : ""} />
        <Gauge label="Disk" value={s ? `${s.disk_percent.toFixed(0)}%` : "…"} pct={s?.disk_percent}
               sub={s ? `${s.disk_free_gb} GB frei` : ""} />
        <Gauge label="FFmpeg" value={s ? String(s.ffmpeg_processes) : "…"} />
      </div>

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Job / Ziel</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3">FPS</th>
              <th className="px-4 py-3">kbit/s</th>
              <th className="px-4 py-3">Speed</th>
              <th className="px-4 py-3">CPU</th>
              <th className="px-4 py-3">RAM</th>
            </tr>
          </thead>
          <tbody>
            {(outputs.data ?? []).map((o) => (
              <tr key={o.output_id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-mist">{o.job_name}<span className="text-slate"> · {o.destination ?? "—"}</span></td>
                <td className="px-4 py-3"><Badge status={o.state}>{o.state}</Badge></td>
                <td className="px-4 py-3 text-slate">{o.fps?.toFixed(0) ?? "—"}</td>
                <td className="px-4 py-3 text-slate">{o.bitrate_kbps?.toFixed(0) ?? "—"}</td>
                <td className={`px-4 py-3 ${o.speed && o.speed < 1 ? "text-warning" : "text-slate"}`}>{o.speed ? `${o.speed.toFixed(2)}×` : "—"}</td>
                <td className="px-4 py-3 text-slate">{o.cpu_pct != null ? `${o.cpu_pct.toFixed(0)}%` : "—"}</td>
                <td className="px-4 py-3 text-slate">{o.rss_mb != null ? `${o.rss_mb.toFixed(0)} MB` : "—"}</td>
              </tr>
            ))}
            {outputs.data?.length === 0 && <tr><td colSpan={7} className="px-4 py-6 text-center text-slate">{t("common.status")}: —</td></tr>}
          </tbody>
        </table>
      </Panel>

      {mtx.data?.enabled && <IngestPanel status={mtx.data} />}
    </div>
  );
}

function IngestPanel({ status }: { status: MediamtxStatus }) {
  const { t } = useTranslation();
  const fmtBytes = (n: number) => {
    if (n < 1024) return `${n} B`;
    if (n < 1024 ** 2) return `${(n / 1024).toFixed(0)} KB`;
    if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
    return `${(n / 1024 ** 3).toFixed(2)} GB`;
  };

  return (
    <Panel className="space-y-3">
      <div className="flex items-center gap-2">
        <h2 className="text-mist">{t("monitoring.ingest.title")}</h2>
        <Badge status={status.reachable ? "running" : "failed"}>
          {status.reachable ? t("monitoring.ingest.online") : t("monitoring.ingest.offline")}
        </Badge>
      </div>

      {!status.reachable && <p className="text-xs text-slate">{t("monitoring.ingest.offlineHint")}</p>}

      {status.reachable && status.paths.length === 0 && (
        <p className="text-xs text-slate">{t("monitoring.ingest.none")}</p>
      )}

      {status.paths.length > 0 && (
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-2 py-2">{t("monitoring.ingest.path")}</th>
              <th className="px-2 py-2">{t("common.status")}</th>
              <th className="px-2 py-2">{t("monitoring.ingest.source")}</th>
              <th className="px-2 py-2">{t("monitoring.ingest.tracks")}</th>
              <th className="px-2 py-2">{t("monitoring.ingest.in")}</th>
              <th className="px-2 py-2">{t("monitoring.ingest.readers")}</th>
            </tr>
          </thead>
          <tbody>
            {status.paths.map((p) => (
              <tr key={p.name} className="border-b border-slate/10">
                <td className="px-2 py-2 text-mist">{p.name}</td>
                <td className="px-2 py-2"><Badge status={p.ready ? "running" : "stopped"}>{p.ready ? t("monitoring.ingest.live") : t("monitoring.ingest.idle")}</Badge></td>
                <td className="px-2 py-2 text-slate">{p.source_type ?? "—"}</td>
                <td className="px-2 py-2 text-slate">{p.tracks.length ? p.tracks.join(", ") : "—"}</td>
                <td className="px-2 py-2 text-slate">{fmtBytes(p.bytes_received)}</td>
                <td className="px-2 py-2 text-slate">{p.readers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Panel>
  );
}

function Gauge({ label, value, pct, sub }: { label: string; value: string; pct?: number; sub?: string }) {
  const color = pct == null ? "text-mist" : pct > 90 ? "text-danger" : pct > 70 ? "text-warning" : "text-core-green";
  return (
    <Panel className="!p-4">
      <div className="text-xs uppercase tracking-wide text-slate">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${color}`}>{value}</div>
      {sub && <div className="text-xs text-slate mt-1">{sub}</div>}
    </Panel>
  );
}

import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import HelpLink from "../components/HelpLink";
import LogsPanel from "../components/LogsPanel";
import MetadataPanel from "../components/MetadataPanel";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { CommandPreview, Destination, DryRunReport, FFmpegProfile, MediamtxSource, PreflightReport, StreamJob } from "../lib/types";
import { useAsync } from "../lib/useAsync";

// Derive a short, human-readable detail from a check's params. The backend guarantees params
// never contain secrets/stream keys, so any present value is safe to display.
function checkDetail(c: { params: Record<string, unknown> }): string {
  const p = c.params ?? {};
  if (typeof p.detail === "string") return p.detail;
  if (typeof p.codecs === "string") return p.codecs;
  if (typeof p.free_gb === "number") return `${p.free_gb} GB`;
  if (p.version != null) return `${p.version}${p.min != null ? ` (min ${p.min})` : ""}`;
  if (typeof p.provider === "string") return p.provider;
  if (typeof p.destination === "string") return p.destination;
  return "";
}

export default function StreamJobsPage() {
  const { t } = useTranslation();
  const isAdmin = useAuthStore((s) => s.hasRole("admin"));
  const jobs = useAsync<StreamJob[]>(() => api.get("/stream-jobs"), []);
  const profiles = useAsync<FFmpegProfile[]>(() => api.get("/ffmpeg-profiles"), []);
  const destinations = useAsync<Destination[]>(() => api.get("/destinations"), []);

  const [showCreate, setShowCreate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<Record<string, string> | null>(null);
  const [logsJob, setLogsJob] = useState<StreamJob | null>(null);
  const [metaJob, setMetaJob] = useState<StreamJob | null>(null);
  const [preflight, setPreflight] = useState<PreflightReport | null>(null);
  const [gate, setGate] = useState<{ id: string; code: string } | null>(null);
  const [dryRun, setDryRun] = useState<DryRunReport | null>(null);
  const [dryBusy, setDryBusy] = useState(false);

  const runDryRun = async (id: string) => {
    setError(null); setDryRun(null); setDryBusy(true);
    try {
      setDryRun(await api.post<DryRunReport>(`/stream-jobs/${id}/dry-run`));
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    } finally {
      setDryBusy(false);
    }
  };

  const act = async (id: string, action: "start" | "stop" | "restart", override = false) => {
    setError(null);
    if (action === "start") setGate(null);
    const path = action === "start" && override
      ? `/stream-jobs/${id}/start?override=true`
      : `/stream-jobs/${id}/${action}`;
    try {
      const res = await api.post<CommandPreview>(path);
      if (res?.previews) setPreview(res.previews);
      jobs.reload();
    } catch (e) {
      if (e instanceof ApiException) {
        if (action === "start" && (e.code === "preflight.required" || e.code === "preflight.blocked")) {
          setGate({ id, code: e.code });
        } else {
          setError(e.localized);
        }
      }
    }
  };

  const showPreview = async (id: string) => {
    setError(null);
    try {
      const res = await api.post<CommandPreview>(`/stream-jobs/${id}/preview`);
      setPreview(res.previews);
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    }
  };

  const runPreflight = async (id: string) => {
    setError(null);
    try {
      setPreflight(await api.post<PreflightReport>(`/stream-jobs/${id}/preflight`));
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    }
  };

  const remove = async (id: string) => {
    await api.del(`/stream-jobs/${id}`);
    jobs.reload();
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
          {t("nav.streamJobs")} <HelpLink page="user-guide/streams.md" />
        </h1>
        <Button onClick={() => setShowCreate((v) => !v)}>{t("common.create")}</Button>
      </header>

      {error && <p className="text-danger text-sm">{error}</p>}

      {showCreate && (
        <CreateJobForm
          profiles={profiles.data ?? []}
          destinations={destinations.data ?? []}
          onCreated={() => { setShowCreate(false); jobs.reload(); }}
          onError={setError}
        />
      )}

      {logsJob && (
        <LogsPanel jobId={logsJob.id} jobName={logsJob.name} onClose={() => setLogsJob(null)} />
      )}

      {metaJob && (
        <MetadataPanel jobId={metaJob.id} jobName={metaJob.name} onClose={() => setMetaJob(null)} />
      )}

      {gate && (
        <Panel>
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-warning">
              {t(`preflight.gate.${gate.code === "preflight.required" ? "required" : "blocked"}`)}
            </p>
            <div className="flex items-center gap-2">
              {isAdmin && (
                <Button variant="danger" onClick={() => act(gate.id, "start", true)}>
                  {t("preflight.gate.override")}
                </Button>
              )}
              <button className="text-xs text-slate hover:text-mist" onClick={() => setGate(null)}>✕</button>
            </div>
          </div>
        </Panel>
      )}

      {preflight && (
        <Panel>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-mist text-sm flex items-center gap-2">
              {t("nav.preflight")} <Badge status={preflight.level} />
              {preflight.stale && <span className="text-xs text-warning">{t("preflight.stale")}</span>}
              <span className={`text-xs ${preflight.can_start ? "text-success" : "text-danger"}`}>
                {preflight.can_start ? t("preflight.canStart") : t("preflight.cannotStart")}
              </span>
            </h2>
            <button className="text-xs text-slate hover:text-mist" onClick={() => setPreflight(null)}>✕</button>
          </div>
          <div className="flex gap-4 text-xs mb-3 text-slate">
            <span className="text-danger">{t("preflight.summary.critical")}: {preflight.summary.critical ?? 0}</span>
            <span className="text-warning">{t("preflight.summary.warning")}: {preflight.summary.warning ?? 0}</span>
            <span className="text-success">{t("preflight.summary.ok")}: {preflight.summary.ok ?? 0}</span>
          </div>
          <ul className="space-y-2 text-sm">
            {preflight.checks.map((c, i) => (
              <li key={i} className="flex items-center justify-between border-b border-slate/10 pb-2">
                <span className="text-mist flex items-center gap-2">
                  {t(`preflight.${c.code}`, { defaultValue: c.code })}
                  {c.blocking && <span className="text-[10px] uppercase text-danger">{t("preflight.blocking")}</span>}
                </span>
                <span className="flex items-center gap-2">
                  {checkDetail(c) && <span className="text-slate text-xs">{checkDetail(c)}</span>}
                  <Badge status={c.level === "ok" ? "green" : c.level === "warn" ? "yellow" : "red"} />
                </span>
              </li>
            ))}
          </ul>
        </Panel>
      )}

      {dryRun && (
        <Panel>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-mist text-sm flex items-center gap-2">
              {t("dryRun.title")} <Badge status={dryRun.ok ? "green" : "red"}>{dryRun.ok ? "ok" : "fail"}</Badge>
            </h2>
            <button className="text-xs text-slate hover:text-mist" onClick={() => setDryRun(null)}>✕</button>
          </div>
          <div className="flex gap-6 text-sm mb-2">
            <span className="text-slate">Speed: <span className={dryRun.speed != null && dryRun.speed < 1 ? "text-warning" : "text-mist"}>{dryRun.speed != null ? `${dryRun.speed}×` : "—"}</span></span>
            <span className="text-slate">FPS: <span className="text-mist">{dryRun.fps ?? "—"}</span></span>
          </div>
          <p className={`text-sm ${dryRun.ok ? "text-mist" : "text-danger"}`}>{dryRun.message}</p>
          {dryRun.log_tail.length > 0 && (
            <pre className="mt-2 text-xs text-slate whitespace-pre-wrap break-all bg-deep-navy rounded p-3 max-h-48 overflow-auto">{dryRun.log_tail.join("\n")}</pre>
          )}
        </Panel>
      )}

      {preview && (
        <Panel>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-mist text-sm">{t("ffmpeg.commandPreview")}</h2>
            <button className="text-xs text-slate hover:text-mist" onClick={() => setPreview(null)}>✕</button>
          </div>
          {Object.entries(preview).map(([oid, cmd]) => (
            <pre key={oid} className="text-xs text-signal-cyan whitespace-pre-wrap break-all bg-deep-navy rounded p-3 mb-2">
              {cmd}
            </pre>
          ))}
        </Panel>
      )}

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">{t("common.create")}</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(jobs.data ?? []).map((job) => (
              <tr key={job.id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-mist">{job.name}</td>
                <td className="px-4 py-3"><Badge status={job.status} /></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => showPreview(job.id)}>⌘</Button>
                    <Button variant="ghost" onClick={() => setLogsJob(job)}>{t("nav.logs")}</Button>
                    <Button variant="ghost" onClick={() => setMetaJob(job)}>Meta</Button>
                    <Button variant="ghost" onClick={() => runPreflight(job.id)}>{t("nav.preflight")}</Button>
                    <Button variant="ghost" disabled={dryBusy} onClick={() => runDryRun(job.id)}>{t("dryRun.button")}</Button>
                    <Button variant="ghost" onClick={() => act(job.id, "start")}>{t("common.start")}</Button>
                    <Button variant="ghost" onClick={() => act(job.id, "stop")}>{t("common.stop")}</Button>
                    <Button variant="ghost" onClick={() => act(job.id, "restart")}>{t("common.restart")}</Button>
                    <Button variant="danger" onClick={() => remove(job.id)}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {jobs.data?.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-6 text-center text-slate">—</td></tr>
            )}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function CreateJobForm({
  profiles, destinations, onCreated, onError,
}: {
  profiles: FFmpegProfile[];
  destinations: Destination[];
  onCreated: () => void;
  onError: (msg: string) => void;
}) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [profileId, setProfileId] = useState("");
  const [destId, setDestId] = useState("");
  const [uri, setUri] = useState("");
  const [lavfi, setLavfi] = useState(false);
  const [fromIngest, setFromIngest] = useState(false);
  const [format, setFormat] = useState("flv");
  const [recording, setRecording] = useState(false);
  const [autoRestart, setAutoRestart] = useState(false);
  const [maxRetry, setMaxRetry] = useState(3);
  const [busy, setBusy] = useState(false);
  const ingest = useAsync<MediamtxSource[]>(() => api.get("/mediamtx/sources"), []);

  const pickIngest = (url: string) => {
    if (!url) return;
    setUri(url);
    setLavfi(false);
    setFromIngest(true);
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const input = lavfi
        ? { kind: "url", uri, options: { f: "lavfi" } }
        : fromIngest
        ? { kind: "url", uri, options: { rtsp_transport: "tcp" }, reconnect: true }
        : { kind: "file", uri, options: {} };
      await api.post("/stream-jobs", {
        name,
        ffmpeg_profile_id: profileId || null,
        recording_enabled: recording,
        fallback_policy: autoRestart ? { auto_restart: true, max_retry: maxRetry, retry_delay_s: 5 } : {},
        inputs: [input],
        outputs: [{ destination_id: destId || null, format }],
      });
      onCreated();
    } catch (err) {
      if (err instanceof ApiException) onError(err.localized);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Panel>
      <form onSubmit={submit} className="grid grid-cols-2 gap-4">
        <Field label="Name">
          <Input value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="FFmpeg Profile">
          <Select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
            <option value="">—</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        </Field>
        <Field label="Input URI">
          <Input value={uri} onChange={(e) => { setUri(e.target.value); setFromIngest(false); }} placeholder="testsrc=size=640x480:rate=25" required />
          {(ingest.data?.length ?? 0) > 0 && (
            <Select className="mt-2" value="" onChange={(e) => pickIngest(e.target.value)}>
              <option value="">{t("streamForm.fromIngest")}</option>
              {ingest.data!.map((s) => (
                <option key={s.name} value={s.pull_url}>
                  {s.name}{s.source_type ? ` (${s.source_type})` : ""}
                </option>
              ))}
            </Select>
          )}
        </Field>
        <Field label="Destination">
          <Select value={destId} onChange={(e) => setDestId(e.target.value)}>
            <option value="">—</option>
            {destinations.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </Select>
        </Field>
        <Field label="Format">
          <Select value={format} onChange={(e) => setFormat(e.target.value)}>
            {["flv", "hls", "mpegts", "mp4"].map((f) => <option key={f} value={f}>{f}</option>)}
          </Select>
        </Field>
        <label className="flex items-end gap-2 text-sm text-mist">
          <input type="checkbox" checked={lavfi} onChange={(e) => setLavfi(e.target.checked)} />
          lavfi input (-f lavfi)
        </label>
        <label className="flex items-end gap-2 text-sm text-mist">
          <input type="checkbox" checked={recording} onChange={(e) => setRecording(e.target.checked)} />
          ⏺ {t("nav.recordings")}
        </label>
        <label className="flex items-end gap-2 text-sm text-mist">
          <input type="checkbox" checked={autoRestart} onChange={(e) => setAutoRestart(e.target.checked)} />
          ♻ {t("streamForm.autoRestart")}
        </label>
        {autoRestart && (
          <Field label={t("streamForm.maxRetry")}>
            <Input type="number" min={1} value={maxRetry} onChange={(e) => setMaxRetry(Number(e.target.value))} />
          </Field>
        )}
        <div className="col-span-2">
          <Button type="submit" disabled={busy}>{busy ? t("common.loading") : t("common.create")}</Button>
        </div>
      </form>
    </Panel>
  );
}

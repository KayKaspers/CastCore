import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import LogsPanel from "../components/LogsPanel";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { CommandPreview, Destination, FFmpegProfile, StreamJob } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function StreamJobsPage() {
  const { t } = useTranslation();
  const jobs = useAsync<StreamJob[]>(() => api.get("/stream-jobs"), []);
  const profiles = useAsync<FFmpegProfile[]>(() => api.get("/ffmpeg-profiles"), []);
  const destinations = useAsync<Destination[]>(() => api.get("/destinations"), []);

  const [showCreate, setShowCreate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<Record<string, string> | null>(null);
  const [logsJob, setLogsJob] = useState<StreamJob | null>(null);

  const act = async (id: string, action: "start" | "stop" | "restart") => {
    setError(null);
    try {
      const res = await api.post<CommandPreview>(`/stream-jobs/${id}/${action}`);
      if (res?.previews) setPreview(res.previews);
      jobs.reload();
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
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

  const remove = async (id: string) => {
    await api.del(`/stream-jobs/${id}`);
    jobs.reload();
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist">{t("nav.streamJobs")}</h1>
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
  const [format, setFormat] = useState("flv");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/stream-jobs", {
        name,
        ffmpeg_profile_id: profileId || null,
        inputs: [{ kind: lavfi ? "url" : "file", uri, options: lavfi ? { f: "lavfi" } : {} }],
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
          <Input value={uri} onChange={(e) => setUri(e.target.value)} placeholder="testsrc=size=640x480:rate=25" required />
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
        <div className="col-span-2">
          <Button type="submit" disabled={busy}>{busy ? t("common.loading") : t("common.create")}</Button>
        </div>
      </form>
    </Panel>
  );
}

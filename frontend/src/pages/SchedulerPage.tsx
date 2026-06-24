import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { SchedulerEntry, StorageSource, StreamJob } from "../lib/types";
import { useAsync } from "../lib/useAsync";

const ACTIONS = ["stream_start", "stream_stop", "backup", "scan"];

function describe(e: SchedulerEntry): string {
  if (e.schedule_type === "interval") return `alle ${e.interval_minutes} min`;
  if (e.schedule_type === "daily") return `täglich ${e.daily_time} UTC`;
  if (e.schedule_type === "once") return `einmalig ${e.run_at ? new Date(e.run_at).toLocaleString() : ""}`;
  return e.schedule_type;
}

export default function SchedulerPage() {
  const { t } = useTranslation();
  const entries = useAsync<SchedulerEntry[]>(() => api.get("/scheduler"), []);
  const jobs = useAsync<StreamJob[]>(() => api.get("/stream-jobs"), []);
  const sources = useAsync<StorageSource[]>(() => api.get("/storage-sources"), []);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const runNow = async (id: string) => {
    setError(null);
    try { await api.post(`/scheduler/${id}/run`); entries.reload(); } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.scheduler")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <NewEntry jobs={jobs.data ?? []} sources={sources.data ?? []} onDone={() => entries.reload()} onError={onErr} />

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Aktion</th>
              <th className="px-4 py-3">Zeitplan</th>
              <th className="px-4 py-3">Nächster Lauf</th>
              <th className="px-4 py-3">Letzter Status</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(entries.data ?? []).map((e) => (
              <tr key={e.id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-mist">{e.name} {!e.enabled && <Badge status="stopped">off</Badge>}</td>
                <td className="px-4 py-3 text-slate">{e.action}</td>
                <td className="px-4 py-3 text-slate">{describe(e)}</td>
                <td className="px-4 py-3 text-slate">{e.next_run_at ? new Date(e.next_run_at).toLocaleString() : "—"}</td>
                <td className="px-4 py-3">{e.last_status && <Badge status={e.last_status === "ok" ? "green" : "failed"}>{e.last_status}</Badge>}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => runNow(e.id)}>run</Button>
                    <Button variant="danger" onClick={() => api.del(`/scheduler/${e.id}`).then(() => entries.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {entries.data?.length === 0 && <tr><td colSpan={6} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function NewEntry({ jobs, sources, onDone, onError }: {
  jobs: StreamJob[]; sources: StorageSource[]; onDone: () => void; onError: (e: unknown) => void;
}) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [action, setAction] = useState("stream_start");
  const [targetId, setTargetId] = useState("");
  const [scheduleType, setScheduleType] = useState("daily");
  const [intervalMin, setIntervalMin] = useState(60);
  const [dailyTime, setDailyTime] = useState("20:00");
  const [runAt, setRunAt] = useState("");

  const needsJob = action === "stream_start" || action === "stream_stop";
  const needsSource = action === "scan";

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/scheduler", {
        name, action,
        target_id: needsJob || needsSource ? targetId || null : null,
        schedule_type: scheduleType,
        interval_minutes: scheduleType === "interval" ? intervalMin : 0,
        daily_time: scheduleType === "daily" ? dailyTime : null,
        run_at: scheduleType === "once" && runAt ? new Date(runAt).toISOString() : null,
      });
      setName("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">{t("common.create")}</h2>
      <form onSubmit={submit} className="grid grid-cols-3 gap-3 items-end">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Aktion">
          <Select value={action} onChange={(e) => { setAction(e.target.value); setTargetId(""); }}>
            {ACTIONS.map((a) => <option key={a} value={a}>{a}</option>)}
          </Select>
        </Field>
        <Field label="Ziel">
          <Select value={targetId} onChange={(e) => setTargetId(e.target.value)} disabled={!needsJob && !needsSource}>
            <option value="">{needsJob || needsSource ? "—" : "n/a"}</option>
            {needsJob && jobs.map((j) => <option key={j.id} value={j.id}>{j.name}</option>)}
            {needsSource && sources.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
        </Field>

        <Field label="Typ">
          <Select value={scheduleType} onChange={(e) => setScheduleType(e.target.value)}>
            <option value="daily">täglich</option>
            <option value="interval">Intervall</option>
            <option value="once">einmalig</option>
          </Select>
        </Field>
        {scheduleType === "daily" && (
          <Field label="Uhrzeit (UTC)"><Input type="time" value={dailyTime} onChange={(e) => setDailyTime(e.target.value)} /></Field>
        )}
        {scheduleType === "interval" && (
          <Field label="Minuten"><Input type="number" min={1} value={intervalMin} onChange={(e) => setIntervalMin(Number(e.target.value))} /></Field>
        )}
        {scheduleType === "once" && (
          <Field label="Zeitpunkt"><Input type="datetime-local" value={runAt} onChange={(e) => setRunAt(e.target.value)} /></Field>
        )}
        <div className={scheduleType === "daily" || scheduleType === "interval" || scheduleType === "once" ? "" : "col-span-2"}>
          <Button type="submit">{t("common.create")}</Button>
        </div>
      </form>
    </Panel>
  );
}

import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { NotificationChannel } from "../lib/types";
import { useAsync } from "../lib/useAsync";

const CHANNEL_FIELDS: Record<string, { key: string; secret?: boolean }[]> = {
  webhook: [{ key: "url" }],
  discord: [{ key: "url" }],
  slack: [{ key: "url" }],
  gotify: [{ key: "url" }, { key: "token", secret: true }],
  telegram: [{ key: "bot_token", secret: true }, { key: "chat_id" }],
  email: [{ key: "host" }, { key: "port" }, { key: "from" }, { key: "to" }, { key: "username" }, { key: "password", secret: true }],
};

export default function NotificationsPage() {
  const { t } = useTranslation();
  const list = useAsync<NotificationChannel[]>(() => api.get("/notifications"), []);
  const events = useAsync<string[]>(() => api.get("/notifications/events"), []);
  const [error, setError] = useState<string | null>(null);
  const [testMsg, setTestMsg] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const test = async (n: NotificationChannel) => {
    setTestMsg(null);
    try {
      const r = await api.post<{ ok: boolean; detail: string | null }>(`/notifications/${n.id}/test`);
      setTestMsg(r.ok ? `✓ ${n.name}: gesendet` : `✗ ${n.name}: ${r.detail}`);
    } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.notifications")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}
      {testMsg && <p className="text-sm text-signal-cyan">{testMsg}</p>}

      <NewNotification events={events.data ?? []} onDone={() => list.reload()} onError={onErr} />

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Kanal</th>
              <th className="px-4 py-3">Events</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(list.data ?? []).map((n) => (
              <tr key={n.id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-mist">{n.name} {!n.enabled && <Badge status="stopped">off</Badge>}</td>
                <td className="px-4 py-3 text-slate">{n.channel} {n.has_secret && <span className="text-xs">🔒</span>}</td>
                <td className="px-4 py-3"><div className="flex flex-wrap gap-1">{n.events.map((e) => <Badge key={e} status="pending">{e}</Badge>)}</div></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => test(n)}>{t("common.test")}</Button>
                    <Button variant="danger" onClick={() => api.del(`/notifications/${n.id}`).then(() => list.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {list.data?.length === 0 && <tr><td colSpan={4} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function NewNotification({ events, onDone, onError }: { events: string[]; onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [channel, setChannel] = useState("discord");
  const [secret, setSecret] = useState<Record<string, string>>({});
  const [selEvents, setSelEvents] = useState<string[]>(["stream_started", "stream_failed"]);

  const fields = CHANNEL_FIELDS[channel] ?? [];

  const toggle = (e: string) =>
    setSelEvents((p) => (p.includes(e) ? p.filter((x) => x !== e) : [...p, e]));

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    try {
      await api.post("/notifications", { name, channel, events: selEvents, secret });
      setName(""); setSecret({});
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">{t("common.create")}</h2>
      <form onSubmit={submit} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
          <Field label="Kanal">
            <Select value={channel} onChange={(e) => { setChannel(e.target.value); setSecret({}); }}>
              {Object.keys(CHANNEL_FIELDS).map((c) => <option key={c} value={c}>{c}</option>)}
            </Select>
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {fields.map((f) => (
            <Field key={f.key} label={f.key}>
              <Input type={f.secret ? "password" : "text"} value={secret[f.key] ?? ""}
                     onChange={(e) => setSecret((p) => ({ ...p, [f.key]: e.target.value }))} />
            </Field>
          ))}
        </div>
        <div>
          <span className="text-xs uppercase tracking-wide text-slate">Events</span>
          <div className="flex flex-wrap gap-3 mt-1">
            {events.map((e) => (
              <label key={e} className="flex items-center gap-1 text-sm text-mist">
                <input type="checkbox" checked={selEvents.includes(e)} onChange={() => toggle(e)} /> {e}
              </label>
            ))}
          </div>
        </div>
        <Button type="submit">{t("common.create")}</Button>
      </form>
    </Panel>
  );
}

import { FormEvent, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Link } from "react-router-dom";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { Destination, PlatformAccount, PlatformProvider } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function ResourcesPage() {
  const { t } = useTranslation();
  const destinations = useAsync<Destination[]>(() => api.get("/destinations"), []);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.platforms")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <ConnectedPlatforms onError={onErr} />

      <p className="text-sm text-slate">
        FFmpeg-Profile findest du jetzt unter <Link to="/profiles" className="text-signal-cyan hover:underline">FFmpeg-Profile</Link>.
      </p>

      <section className="space-y-3">
        <h2 className="text-mist">Destinations</h2>
        <NewDestination onDone={() => destinations.reload()} onError={onErr} />
        <Panel className="!p-0 overflow-hidden">
          <ul>
            {(destinations.data ?? []).map((d) => (
              <li key={d.id} className="flex items-center justify-between px-4 py-3 border-b border-slate/10">
                <span className="text-mist text-sm">{d.name} <span className="text-slate">· {d.kind}</span></span>
                <div className="flex items-center gap-3">
                  {d.has_stream_key && <Badge status="pending">key ••••</Badge>}
                  <Button variant="danger" onClick={() => api.del(`/destinations/${d.id}`).then(() => destinations.reload())}>✕</Button>
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </section>
    </div>
  );
}

function ConnectedPlatforms({ onError }: { onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const providers = useAsync<PlatformProvider[]>(() => api.get("/oauth/providers"), []);
  const accounts = useAsync<PlatformAccount[]>(() => api.get("/platform-accounts"), []);
  const [notice, setNotice] = useState<string | null>(null);

  // Surface the result of the OAuth redirect (?connected=… / ?error=oauth).
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    if (q.get("connected")) setNotice(t("platforms.connected", { provider: q.get("connected") }));
    else if (q.get("error") === "oauth") setNotice(t("platforms.connectError"));
    if (q.get("connected") || q.get("error")) {
      window.history.replaceState({}, "", window.location.pathname);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const connect = async (provider: string) => {
    try {
      const { authorize_url } = await api.post<{ authorize_url: string }>(`/oauth/${provider}/authorize`);
      window.location.href = authorize_url; // full-page redirect to the provider
    } catch (e) { onError(e); }
  };

  const disconnect = async (id: string) => {
    if (!window.confirm(t("platforms.disconnectConfirm"))) return;
    try { await api.del(`/platform-accounts/${id}`); accounts.reload(); } catch (e) { onError(e); }
  };

  const enabled = (providers.data ?? []).filter((p) => p.enabled);
  const disabled = (providers.data ?? []).filter((p) => !p.enabled);

  return (
    <section className="space-y-3">
      <h2 className="text-mist">{t("platforms.connectedTitle")}</h2>
      {notice && <p className="text-core-green text-sm">{notice}</p>}
      <p className="text-xs text-slate">{t("platforms.intro")}</p>

      <div className="flex flex-wrap gap-2">
        {enabled.map((p) => (
          <Button key={p.provider} variant="ghost" onClick={() => connect(p.provider)}>
            + {t("platforms.connect", { provider: p.provider })}
          </Button>
        ))}
        {enabled.length === 0 && <p className="text-xs text-slate">{t("platforms.noneEnabled")}</p>}
      </div>

      {disabled.length > 0 && (
        <p className="text-xs text-slate">
          {t("platforms.disabledHint", { providers: disabled.map((p) => p.provider).join(", ") })}
        </p>
      )}

      <Panel className="!p-0 overflow-hidden">
        <ul>
          {(accounts.data ?? []).map((a) => (
            <li key={a.id} className="flex items-center justify-between px-4 py-3 border-b border-slate/10">
              <span className="text-mist text-sm">
                {a.account_name || a.provider} <span className="text-slate">· {a.provider}</span>
                {a.has_refresh && <Badge status="running">{t("platforms.linked")}</Badge>}
              </span>
              <Button variant="danger" onClick={() => disconnect(a.id)}>{t("platforms.disconnect")}</Button>
            </li>
          ))}
          {accounts.data?.length === 0 && (
            <li className="px-4 py-3 text-xs text-slate">{t("platforms.noAccounts")}</li>
          )}
        </ul>
      </Panel>
    </section>
  );
}

function NewDestination({ onDone, onError }: { onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [kind, setKind] = useState("rtmp");
  const [url, setUrl] = useState("");
  const [key, setKey] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/destinations", { name, kind, url, stream_key: key || null });
      setName(""); setUrl(""); setKey("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <form onSubmit={submit} className="grid grid-cols-2 gap-3 items-end">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Kind">
          <Select value={kind} onChange={(e) => setKind(e.target.value)}>
            {["rtmp", "platform", "hls", "recording", "preview"].map((k) => <option key={k}>{k}</option>)}
          </Select>
        </Field>
        <Field label="URL"><Input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="rtmp://… or /data/recordings/out.mp4" required /></Field>
        <Field label="Stream key (optional)"><Input type="password" value={key} onChange={(e) => setKey(e.target.value)} /></Field>
        <div className="col-span-2"><Button type="submit">{t("common.create")}</Button></div>
      </form>
    </Panel>
  );
}

import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { Destination, FFmpegProfile } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function ResourcesPage() {
  const { t } = useTranslation();
  const profiles = useAsync<FFmpegProfile[]>(() => api.get("/ffmpeg-profiles"), []);
  const destinations = useAsync<Destination[]>(() => api.get("/destinations"), []);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.platforms")} & {t("nav.streamJobs")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <section className="space-y-3">
        <h2 className="text-mist">FFmpeg Profiles</h2>
        <NewProfile onDone={() => profiles.reload()} onError={onErr} />
        <Panel className="!p-0 overflow-hidden">
          <ul>
            {(profiles.data ?? []).map((p) => (
              <li key={p.id} className="flex items-center justify-between px-4 py-3 border-b border-slate/10">
                <span className="text-mist text-sm">{p.name}</span>
                <div className="flex items-center gap-3">
                  <Badge status={p.copy_mode ? "pending" : "green"}>{p.copy_mode ? "copy" : "encode"}</Badge>
                  <Button variant="danger" onClick={() => api.del(`/ffmpeg-profiles/${p.id}`).then(() => profiles.reload())}>✕</Button>
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </section>

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

function NewProfile({ onDone, onError }: { onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [copy, setCopy] = useState(false);
  const [codec, setCodec] = useState("libx264");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/ffmpeg-profiles", {
        name, copy_mode: copy,
        video: copy ? {} : { codec, preset: "veryfast", bitrate: "4000k" },
        audio: copy ? {} : { codec: "aac", bitrate: "160k" },
      });
      setName("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <form onSubmit={submit} className="grid grid-cols-3 gap-3 items-end">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Video codec">
          <Select value={codec} disabled={copy} onChange={(e) => setCodec(e.target.value)}>
            {["libx264", "libx265", "h264_nvenc", "h264_vaapi"].map((c) => <option key={c}>{c}</option>)}
          </Select>
        </Field>
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-mist">
            <input type="checkbox" checked={copy} onChange={(e) => setCopy(e.target.checked)} /> copy
          </label>
          <Button type="submit">{t("common.create")}</Button>
        </div>
      </form>
    </Panel>
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

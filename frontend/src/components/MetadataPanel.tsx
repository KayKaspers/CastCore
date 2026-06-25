import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api, ApiException } from "../lib/api";
import { Badge, Button, Field, Input, Panel, Select } from "./ui";

const PLATFORMS = ["twitch", "youtube", "kick", "facebook", "custom"];
const PLACEHOLDERS = "{stream_title} {date} {time} {platform} {category} {tags} {source_name} {server_name} {channel_name}";

interface Meta {
  platform: string;
  title: string | null;
  description_template: string | null;
  category: string | null;
  tags: string[];
  language: string | null;
  visibility: string;
}

interface Resolved {
  title: string;
  description: string;
  warnings: string[];
}

export default function MetadataPanel({ jobId, jobName, onClose }: { jobId: string; jobName: string; onClose: () => void }) {
  const { t } = useTranslation();
  const [platform, setPlatform] = useState("twitch");
  const [all, setAll] = useState<Meta[]>([]);
  const [form, setForm] = useState<Meta>({ platform, title: "", description_template: "", category: "", tags: [], language: "de", visibility: "public" });
  const [resolved, setResolved] = useState<Resolved | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tagsStr, setTagsStr] = useState("");

  const loadAll = () => api.get<Meta[]>(`/stream-jobs/${jobId}/metadata`).then(setAll).catch(() => undefined);
  useEffect(() => { loadAll(); /* eslint-disable-next-line */ }, [jobId]);

  useEffect(() => {
    const existing = all.find((m) => m.platform === platform);
    const f = existing ?? { platform, title: "", description_template: "", category: "", tags: [], language: "de", visibility: "public" };
    setForm({ ...f, platform });
    setTagsStr((f.tags ?? []).join(", "));
    setResolved(null);
  }, [platform, all]);

  const save = async () => {
    setError(null);
    try {
      await api.put(`/stream-jobs/${jobId}/metadata/${platform}`, {
        title: form.title || null,
        description_template: form.description_template || null,
        category: form.category || null,
        tags: tagsStr.split(",").map((s) => s.trim()).filter(Boolean),
        language: form.language || null,
        visibility: form.visibility,
      });
      await loadAll();
    } catch (e) { if (e instanceof ApiException) setError(e.localized); }
  };

  const resolve = async () => {
    setError(null);
    try { setResolved(await api.get<Resolved>(`/stream-jobs/${jobId}/metadata/${platform}/resolved`)); }
    catch (e) { if (e instanceof ApiException) setError(e.localized); }
  };

  return (
    <Panel>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-mist text-sm">Plattform-Metadaten · <span className="text-slate">{jobName}</span></h2>
        <button className="text-xs text-slate hover:text-mist" onClick={onClose}>✕</button>
      </div>
      {error && <p className="text-danger text-sm mb-2">{error}</p>}

      <div className="grid grid-cols-2 gap-3">
        <Field label="Plattform">
          <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            {PLATFORMS.map((p) => <option key={p} value={p}>{p}{all.some((m) => m.platform === p) ? " ✓" : ""}</option>)}
          </Select>
        </Field>
        <Field label="Sichtbarkeit">
          <Select value={form.visibility} onChange={(e) => setForm({ ...form, visibility: e.target.value })}>
            {["public", "unlisted", "private"].map((v) => <option key={v} value={v}>{v}</option>)}
          </Select>
        </Field>
        <Field label="Titel"><Input value={form.title ?? ""} onChange={(e) => setForm({ ...form, title: e.target.value })} /></Field>
        <Field label="Kategorie"><Input value={form.category ?? ""} onChange={(e) => setForm({ ...form, category: e.target.value })} /></Field>
        <Field label="Tags (Komma)"><Input value={tagsStr} onChange={(e) => setTagsStr(e.target.value)} /></Field>
        <Field label="Sprache"><Input value={form.language ?? ""} onChange={(e) => setForm({ ...form, language: e.target.value })} /></Field>
        <div className="col-span-2">
          <Field label="Beschreibungsvorlage">
            <textarea
              className="w-full bg-deep-navy border border-slate/40 rounded-md px-3 py-2 text-sm text-mist focus:outline-none focus:border-core-green h-24"
              value={form.description_template ?? ""}
              onChange={(e) => setForm({ ...form, description_template: e.target.value })}
            />
          </Field>
          <p className="text-xs text-slate mt-1">Platzhalter: <span className="font-mono text-signal-cyan">{PLACEHOLDERS}</span></p>
        </div>
      </div>

      <div className="flex items-center gap-2 mt-4">
        <Button onClick={save}>{t("common.save")}</Button>
        <Button variant="ghost" onClick={resolve}>Vorschau auflösen</Button>
      </div>

      {resolved && (
        <div className="mt-4 cc-panel p-3 space-y-2">
          {resolved.warnings.length > 0 && (
            <div className="flex gap-2">{resolved.warnings.map((w) => <Badge key={w} status="yellow">{w}</Badge>)}</div>
          )}
          <div><span className="text-slate text-xs">Titel:</span> <span className="text-mist">{resolved.title}</span></div>
          <div><span className="text-slate text-xs">Beschreibung:</span><pre className="text-mist text-xs whitespace-pre-wrap mt-1">{resolved.description}</pre></div>
        </div>
      )}
    </Panel>
  );
}

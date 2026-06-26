import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api, ApiException } from "../lib/api";
import type { Asset } from "../lib/types";
import AuthImg from "./AuthImg";
import HelpLink from "./HelpLink";
import { Badge, Button, Field, Input, Panel, Select } from "./ui";

const PLATFORMS = ["twitch", "youtube", "kick", "facebook", "custom"];
const PUSH_PROVIDERS = ["twitch", "youtube"];

interface PushRef { code: string; params?: Record<string, unknown> }
interface PushResult {
  provider: string;
  status: string; // success | warning | error
  applied: string[];
  warnings: PushRef[];
  error: PushRef | null;
}

interface ReadinessCheck { key: string; level: string; code: string | null; params?: Record<string, unknown> }
interface Readiness { provider: string; level: string; checks: ReadinessCheck[] }
const PLACEHOLDERS = "{stream_title} {date} {time} {platform} {category} {tags} {source_name} {server_name} {channel_name}";

interface Meta {
  platform: string;
  title: string | null;
  description_template: string | null;
  category: string | null;
  tags: string[];
  language: string | null;
  visibility: string;
  thumbnail_asset_id?: string | null;
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
  const [thumbId, setThumbId] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [pushing, setPushing] = useState(false);
  const [push, setPush] = useState<PushResult | null>(null);
  const [testing, setTesting] = useState(false);
  const [ready, setReady] = useState<Readiness | null>(null);

  useEffect(() => { api.get<Asset[]>("/assets").then(setAssets).catch(() => undefined); }, []);

  const loadAll = () => api.get<Meta[]>(`/stream-jobs/${jobId}/metadata`).then(setAll).catch(() => undefined);
  useEffect(() => { loadAll(); /* eslint-disable-next-line */ }, [jobId]);

  useEffect(() => {
    const existing = all.find((m) => m.platform === platform);
    const f = existing ?? { platform, title: "", description_template: "", category: "", tags: [], language: "de", visibility: "public" };
    setForm({ ...f, platform });
    setTagsStr((f.tags ?? []).join(", "));
    setThumbId(f.thumbnail_asset_id ?? "");
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
        thumbnail_asset_id: thumbId || null,
      });
      await loadAll();
    } catch (e) { if (e instanceof ApiException) setError(e.localized); }
  };

  const resolve = async () => {
    setError(null);
    try { setResolved(await api.get<Resolved>(`/stream-jobs/${jobId}/metadata/${platform}/resolved`)); }
    catch (e) { if (e instanceof ApiException) setError(e.localized); }
  };

  // Reset push/readiness results when switching platform.
  useEffect(() => { setPush(null); setReady(null); }, [platform]);

  const testConnection = async () => {
    setError(null); setReady(null); setTesting(true);
    try {
      setReady(await api.post<Readiness>(`/stream-jobs/${jobId}/platforms/${platform}/readiness`));
    } catch (e) { if (e instanceof ApiException) setError(e.localized); }
    finally { setTesting(false); }
  };

  const pushMeta = async () => {
    setError(null); setPush(null); setPushing(true);
    try {
      // save first so the platform gets the current form values
      await save();
      setPush(await api.post<PushResult>(`/stream-jobs/${jobId}/platforms/${platform}/push-metadata`));
    } catch (e) { if (e instanceof ApiException) setError(e.localized); }
    finally { setPushing(false); }
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
        <Field label="Thumbnail (Asset)">
          <Select value={thumbId} onChange={(e) => setThumbId(e.target.value)}>
            <option value="">—</option>
            {assets.map((a) => <option key={a.id} value={a.id}>{a.original_name ?? a.filename}</option>)}
          </Select>
        </Field>
        <div className="flex items-end">
          {thumbId && <AuthImg assetId={thumbId} className="h-16 rounded-md border border-slate/30" />}
        </div>
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
        <Button
          variant="ghost"
          onClick={testConnection}
          disabled={testing || !PUSH_PROVIDERS.includes(platform)}
          title={PUSH_PROVIDERS.includes(platform) ? "" : t("platformPush.unsupported")}
        >
          {testing ? t("common.loading") : t("platformReady.button")}
        </Button>
        <Button
          onClick={pushMeta}
          disabled={pushing || !PUSH_PROVIDERS.includes(platform)}
          title={PUSH_PROVIDERS.includes(platform) ? "" : t("platformPush.unsupported")}
        >
          {pushing ? t("common.loading") : t("platformPush.button")}
        </Button>
      </div>

      {ready && (
        <div className="mt-4 cc-panel p-3 space-y-2">
          <div className="flex items-center gap-2">
            <Badge status={ready.level === "green" ? "running" : ready.level === "yellow" ? "yellow" : "failed"}>
              {t(`platformReady.${ready.level}`)}
            </Badge>
            <span className="text-xs text-slate">{ready.provider}</span>
            <HelpLink page="admin-guide/platform-oauth.md" />
          </div>
          <ul className="space-y-1">
            {ready.checks.map((c) => (
              <li key={c.key} className="text-xs flex items-start gap-2">
                <span className={c.level === "ok" ? "text-core-green" : c.level === "warn" ? "text-warning" : "text-danger"}>
                  {c.level === "ok" ? "✓" : c.level === "warn" ? "!" : "✗"}
                </span>
                <span className="text-mist">{t(`platformReady.check.${c.key}`, c.key)}</span>
                {c.code && <span className="text-slate">— {t(`error.${c.code}`, c.params)}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {push && (
        <div className="mt-4 cc-panel p-3 space-y-2">
          <div className="flex items-center gap-2">
            <Badge status={push.status === "success" ? "running" : push.status === "warning" ? "yellow" : "failed"}>
              {t(`platformPush.${push.status}`)}
            </Badge>
            <span className="text-xs text-slate">{push.provider}</span>
            <HelpLink page="admin-guide/platform-oauth.md" />
          </div>
          {push.applied.length > 0 && (
            <div className="text-xs text-slate">
              {t("platformPush.applied")}: <span className="text-mist">{push.applied.join(", ")}</span>
            </div>
          )}
          {push.warnings.map((w, i) => (
            <p key={i} className="text-warning text-xs">{t(`error.${w.code}`, w.params)}</p>
          ))}
          {push.error && <p className="text-danger text-sm">{t(`error.${push.error.code}`, push.error.params)}</p>}
        </div>
      )}

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

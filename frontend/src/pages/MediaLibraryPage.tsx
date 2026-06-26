import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { MediaItem, ScanResult, StorageSource } from "../lib/types";
import { useAsync } from "../lib/useAsync";

function fmtSize(b: number): string {
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(0)} KB`;
  if (b < 1024 * 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`;
  return `${(b / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

function fmtDur(s: number | null): string {
  if (!s) return "—";
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = Math.floor(s % 60);
  return h > 0 ? `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}` : `${m}:${String(sec).padStart(2, "0")}`;
}

export default function MediaLibraryPage() {
  const { t } = useTranslation();
  const sources = useAsync<StorageSource[]>(() => api.get("/storage-sources"), []);
  const [sourceId, setSourceId] = useState("");
  const [q, setQ] = useState("");
  const [onlyStreamable, setOnlyStreamable] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanMsg, setScanMsg] = useState<string | null>(null);

  const query = useMemo(() => {
    const p = new URLSearchParams();
    if (sourceId) p.set("source_id", sourceId);
    if (q) p.set("q", q);
    if (onlyStreamable) p.set("streamable", "true");
    return p.toString();
  }, [sourceId, q, onlyStreamable]);

  const media = useAsync<MediaItem[]>(() => api.get(`/media?${query}`), [query]);

  const sourceMap = useMemo(() => {
    const m: Record<string, StorageSource> = {};
    for (const s of sources.data ?? []) m[s.id] = s;
    return m;
  }, [sources.data]);

  const scan = async () => {
    if (!sourceId) { setError("Bitte zuerst eine Quelle wählen."); return; }
    setError(null);
    setScanMsg(t("common.loading"));
    try {
      const r = await api.post<ScanResult>(`/media/scan/${sourceId}`);
      setScanMsg(`${r.files} Dateien · ${r.indexed} indexiert · ${r.probed} analysiert`);
      media.reload();
    } catch (e) {
      setScanMsg(null);
      if (e instanceof ApiException) setError(e.localized);
    }
  };

  const copyAbs = (item: MediaItem) => {
    const src = sourceMap[item.storage_source_id];
    const base = src?.effective_path ?? "";
    navigator.clipboard?.writeText(`${base}/${item.rel_path}`.replace(/\\/g, "/"));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.mediaLibrary")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <Panel>
        <div className="grid grid-cols-4 gap-3 items-end">
          <Field label={t("nav.sources")}>
            <Select value={sourceId} onChange={(e) => setSourceId(e.target.value)}>
              <option value="">— {t("common.search")} —</option>
              {(sources.data ?? []).map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </Select>
          </Field>
          <Field label={t("common.search")}>
            <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="*.mp4 …" />
          </Field>
          <label className="flex items-center gap-2 text-sm text-mist">
            <input type="checkbox" checked={onlyStreamable} onChange={(e) => setOnlyStreamable(e.target.checked)} />
            nur streamfähig
          </label>
          <Button onClick={scan}>Scan</Button>
        </div>
        {scanMsg && <p className="text-xs text-signal-cyan mt-2">{scanMsg}</p>}
      </Panel>

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Datei</th>
              <th className="px-4 py-3">Codec</th>
              <th className="px-4 py-3">Auflösung</th>
              <th className="px-4 py-3">Dauer</th>
              <th className="px-4 py-3">Größe</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(media.data ?? []).map((m) => (
              <tr key={m.id} className="border-b border-slate/10">
                <td className="px-4 py-3">
                  <div className="text-mist">
                    {m.filename} {m.streamable && <Badge status="green">stream</Badge>}
                    {m.risky_codec && <Badge status="failed">{t("media.riskyCodec")}</Badge>}
                  </div>
                  <div className="text-xs text-slate">{m.rel_path} · {m.kind}</div>
                </td>
                <td className="px-4 py-3 text-slate">{m.probe?.video_codec ?? "—"}{m.probe?.audio_codec ? ` / ${m.probe.audio_codec}` : ""}</td>
                <td className="px-4 py-3 text-slate">{m.probe?.width ? `${m.probe.width}×${m.probe.height}` : "—"}{m.probe?.fps ? ` @${m.probe.fps}` : ""}</td>
                <td className="px-4 py-3 text-slate">{fmtDur(m.probe?.duration_s ?? null)}</td>
                <td className="px-4 py-3 text-slate">{fmtSize(m.size_bytes)}</td>
                <td className="px-4 py-3 text-right">
                  <button className="text-xs text-slate hover:text-core-green" onClick={() => copyAbs(m)}>copy path</button>
                </td>
              </tr>
            ))}
            {media.data?.length === 0 && <tr><td colSpan={6} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

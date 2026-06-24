import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { MediaItem, Playlist } from "../lib/types";
import { useAsync } from "../lib/useAsync";

function fmtDur(s: number | null): string {
  if (s == null) return "—";
  const m = Math.floor(s / 60), sec = Math.floor(s % 60);
  return `${m}:${String(sec).padStart(2, "0")}`;
}

export default function PlaylistsPage() {
  const { t } = useTranslation();
  const lists = useAsync<Playlist[]>(() => api.get("/playlists"), []);
  const [selId, setSelId] = useState<string | null>(null);
  const detail = useAsync<Playlist>(() => api.get(`/playlists/${selId}`), [selId]);
  const media = useAsync<MediaItem[]>(() => api.get("/media?streamable=true"), []);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState<number | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };
  const refresh = () => { lists.reload(); detail.reload(); };

  const createList = async (e: FormEvent, name: string, mode: string) => {
    e.preventDefault();
    try {
      const p = await api.post<Playlist>("/playlists", { name, mode });
      setSelId(p.id);
      lists.reload();
    } catch (e) { onErr(e); }
  };

  const addItem = async (mediaId: string) => {
    if (!selId || !mediaId) return;
    try { await api.post(`/playlists/${selId}/items`, { media_item_id: mediaId }); refresh(); } catch (e) { onErr(e); }
  };

  const removeItem = async (itemId: string) => {
    if (!selId) return;
    await api.del(`/playlists/${selId}/items/${itemId}`); refresh();
  };

  const move = async (index: number, dir: -1 | 1) => {
    if (!selId || !detail.data?.items) return;
    const ids = detail.data.items.map((i) => i.id);
    const j = index + dir;
    if (j < 0 || j >= ids.length) return;
    [ids[index], ids[j]] = [ids[j], ids[index]];
    await api.post(`/playlists/${selId}/reorder`, { item_ids: ids });
    detail.reload();
  };

  const setMode = async (mode: string) => {
    if (!detail.data) return;
    await api.patch(`/playlists/${selId}`, { name: detail.data.name, mode, description: detail.data.description });
    refresh();
  };

  const resolve = async () => {
    if (!selId) return;
    const r = await api.get<{ total_duration_s: number }>(`/playlists/${selId}/resolve`);
    setTotal(r.total_duration_s);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.playlists")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="space-y-3">
          <CreateList onCreate={createList} />
          <Panel className="!p-0 overflow-hidden">
            <ul>
              {(lists.data ?? []).map((p) => (
                <li key={p.id}
                    className={`px-4 py-3 border-b border-slate/10 cursor-pointer flex items-center justify-between ${selId === p.id ? "bg-core-green/10" : "hover:bg-slate/5"}`}
                    onClick={() => { setSelId(p.id); setTotal(null); }}>
                  <span className="text-mist text-sm">{p.name}</span>
                  <span className="flex items-center gap-2"><Badge status="pending">{p.mode}</Badge><span className="text-xs text-slate">{p.item_count}</span></span>
                </li>
              ))}
              {lists.data?.length === 0 && <li className="px-4 py-6 text-center text-slate">—</li>}
            </ul>
          </Panel>
        </div>

        <div className="lg:col-span-2">
          {detail.data ? (
            <Panel>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-mist">{detail.data.name}</h2>
                <div className="flex items-center gap-3 w-1/2">
                  <Select value={detail.data.mode} onChange={(e) => setMode(e.target.value)}>
                    <option value="sequential">sequential</option>
                    <option value="shuffle">shuffle</option>
                    <option value="loop">loop</option>
                  </Select>
                  <Button variant="ghost" onClick={resolve}>Dauer</Button>
                  {total != null && <span className="text-signal-cyan text-sm">{fmtDur(total)}</span>}
                </div>
              </div>

              <div className="flex items-center gap-2 mb-4">
                <Select onChange={(e) => { addItem(e.target.value); e.target.value = ""; }} defaultValue="">
                  <option value="" disabled>+ Medium aus Bibliothek …</option>
                  {(media.data ?? []).map((m) => <option key={m.id} value={m.id}>{m.filename}</option>)}
                </Select>
              </div>

              <ol className="space-y-1">
                {(detail.data.items ?? []).map((it, idx) => (
                  <li key={it.id} className="flex items-center justify-between px-3 py-2 bg-deep-navy rounded text-sm">
                    <span className="text-mist">{idx + 1}. {it.filename} <span className="text-slate">{fmtDur(it.duration_s)}</span></span>
                    <span className="flex items-center gap-1">
                      <button className="text-slate hover:text-mist px-1" onClick={() => move(idx, -1)}>▲</button>
                      <button className="text-slate hover:text-mist px-1" onClick={() => move(idx, 1)}>▼</button>
                      <button className="text-danger hover:brightness-125 px-1" onClick={() => removeItem(it.id)}>✕</button>
                    </span>
                  </li>
                ))}
                {detail.data.items?.length === 0 && <li className="text-slate text-sm px-3 py-4">Noch keine Medien.</li>}
              </ol>
            </Panel>
          ) : (
            <Panel><p className="text-slate text-sm">Playlist auswählen oder anlegen.</p></Panel>
          )}
        </div>
      </div>
    </div>
  );
}

function CreateList({ onCreate }: { onCreate: (e: FormEvent, name: string, mode: string) => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [mode, setMode] = useState("sequential");
  return (
    <Panel>
      <form onSubmit={(e) => { onCreate(e, name, mode); setName(""); }} className="space-y-3">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Modus">
          <Select value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="sequential">sequential</option>
            <option value="shuffle">shuffle</option>
            <option value="loop">loop</option>
          </Select>
        </Field>
        <Button type="submit" className="w-full">{t("common.create")}</Button>
      </form>
    </Panel>
  );
}

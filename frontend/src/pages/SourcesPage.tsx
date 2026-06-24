import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { BrowseResult, StorageSource, TestResult } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function SourcesPage() {
  const { t } = useTranslation();
  const sources = useAsync<StorageSource[]>(() => api.get("/storage-sources"), []);
  const [error, setError] = useState<string | null>(null);
  const [browse, setBrowse] = useState<{ source: StorageSource; result: BrowseResult } | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const action = async (id: string, verb: "test" | "mount" | "unmount") => {
    setError(null);
    try {
      const res = await api.post<TestResult>(`/storage-sources/${id}/${verb}`);
      if (!res.ok && res.detail) setError(res.detail);
      sources.reload();
    } catch (e) { onErr(e); }
  };

  const openBrowse = async (source: StorageSource, subpath = "") => {
    setError(null);
    try {
      const result = await api.get<BrowseResult>(`/storage-sources/${source.id}/browse?subpath=${encodeURIComponent(subpath)}`);
      setBrowse({ source, result });
    } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist">{t("nav.sources")}</h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <div className="grid lg:grid-cols-2 gap-4">
        <NewLocal onDone={() => sources.reload()} onError={onErr} />
        <NewSmb onDone={() => sources.reload()} onError={onErr} />
      </div>

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(sources.data ?? []).map((s) => (
              <tr key={s.id} className="border-b border-slate/10 align-top">
                <td className="px-4 py-3">
                  <div className="text-mist">{s.name} <span className="text-slate">· {s.type}</span></div>
                  <div className="text-xs text-slate">{s.effective_path}</div>
                  {s.last_error && <div className="text-xs text-danger mt-1">{s.last_error}</div>}
                </td>
                <td className="px-4 py-3"><Badge status={s.status === "online" ? "running" : s.status === "error" ? "failed" : "stopped"}>{s.status}</Badge></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end flex-wrap">
                    <Button variant="ghost" onClick={() => action(s.id, "test")}>{t("common.test")}</Button>
                    {s.type === "smb" && <Button variant="ghost" onClick={() => action(s.id, "mount")}>mount</Button>}
                    {s.type === "smb" && <Button variant="ghost" onClick={() => action(s.id, "unmount")}>unmount</Button>}
                    <Button variant="ghost" onClick={() => openBrowse(s)}>{t("common.search")}</Button>
                    <Button variant="danger" onClick={() => api.del(`/storage-sources/${s.id}`).then(() => sources.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {sources.data?.length === 0 && <tr><td colSpan={3} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>

      {browse && (
        <Panel>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-mist text-sm">{browse.source.name}<span className="text-slate"> · /{browse.result.subpath}</span></h2>
            <button className="text-xs text-slate hover:text-mist" onClick={() => setBrowse(null)}>✕</button>
          </div>
          <ul className="text-sm font-mono">
            {browse.result.subpath && (
              <li className="px-2 py-1 text-signal-cyan cursor-pointer"
                  onClick={() => openBrowse(browse.source, browse.result.subpath.split("/").slice(0, -1).join("/"))}>
                ../
              </li>
            )}
            {browse.result.entries.map((e) => (
              <li key={e.rel_path} className="px-2 py-1 flex items-center justify-between hover:bg-slate/10 rounded">
                <span
                  className={e.is_dir ? "text-signal-cyan cursor-pointer" : "text-mist"}
                  onClick={() => e.is_dir && openBrowse(browse.source, e.rel_path)}
                >
                  {e.is_dir ? "📁 " : ""}{e.name}
                </span>
                <span className="flex items-center gap-2">
                  {e.streamable && <Badge status="green">media</Badge>}
                  {!e.is_dir && (
                    <button className="text-xs text-slate hover:text-core-green"
                            onClick={() => navigator.clipboard?.writeText(e.abs_path)}>
                      copy path
                    </button>
                  )}
                </span>
              </li>
            ))}
          </ul>
          <p className="text-xs text-slate mt-3">
            Tipp: „copy path" → in einem Stream-Job als Input-URI einfügen.
          </p>
        </Panel>
      )}
    </div>
  );
}

function NewLocal({ onDone, onError }: { onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [path, setPath] = useState("/data/media");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/storage-sources/local", { name, path });
      setName("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">Lokale Quelle</h2>
      <form onSubmit={submit} className="space-y-3">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label="Pfad"><Input value={path} onChange={(e) => setPath(e.target.value)} required /></Field>
        <Button type="submit">{t("common.create")}</Button>
      </form>
    </Panel>
  );
}

function NewSmb({ onDone, onError }: { onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [f, setF] = useState({ name: "", server: "", share: "", username: "", password: "", domain: "", smb_version: "3.0" });
  const set = (k: string, v: string) => setF((p) => ({ ...p, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/storage-sources/smb", {
        name: f.name, server: f.server, share: f.share,
        username: f.username || null, password: f.password || null,
        domain: f.domain || null, smb_version: f.smb_version || null,
      });
      setF({ name: "", server: "", share: "", username: "", password: "", domain: "", smb_version: "3.0" });
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">SMB / CIFS</h2>
      <form onSubmit={submit} className="grid grid-cols-2 gap-3">
        <Field label="Name"><Input value={f.name} onChange={(e) => set("name", e.target.value)} required /></Field>
        <Field label="Server / IP"><Input value={f.server} onChange={(e) => set("server", e.target.value)} required /></Field>
        <Field label="Freigabe"><Input value={f.share} onChange={(e) => set("share", e.target.value)} required /></Field>
        <Field label="Domain"><Input value={f.domain} onChange={(e) => set("domain", e.target.value)} /></Field>
        <Field label="Benutzer"><Input value={f.username} onChange={(e) => set("username", e.target.value)} /></Field>
        <Field label="Passwort"><Input type="password" value={f.password} onChange={(e) => set("password", e.target.value)} /></Field>
        <div className="col-span-2"><Button type="submit">{t("common.create")}</Button></div>
      </form>
    </Panel>
  );
}

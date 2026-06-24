import { useTranslation } from "react-i18next";

import { Badge, Button, Panel } from "../components/ui";
import { api } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { Recording } from "../lib/types";
import { useAsync } from "../lib/useAsync";

function fmtSize(b: number): string {
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(0)} KB`;
  if (b < 1024 * 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`;
  return `${(b / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

function fmtDur(s: number | null): string {
  if (s == null) return "—";
  const m = Math.floor(s / 60), sec = Math.floor(s % 60);
  return `${m}:${String(sec).padStart(2, "0")}`;
}

export default function RecordingsPage() {
  const { t } = useTranslation();
  const recs = useAsync<Recording[]>(() => api.get("/recordings"), []);

  const download = async (r: Recording) => {
    const token = useAuthStore.getState().accessToken;
    const res = await fetch(`/api/v1/recordings/${r.id}/download`, { headers: { authorization: `Bearer ${token}` } });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = r.filename; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist">{t("nav.recordings")}</h1>
        <Button variant="ghost" onClick={() => recs.reload()}>↻</Button>
      </header>

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Datei</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3">Dauer</th>
              <th className="px-4 py-3">Größe</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(recs.data ?? []).map((r) => (
              <tr key={r.id} className="border-b border-slate/10">
                <td className="px-4 py-3">
                  <div className="text-mist font-mono text-xs">{r.filename}</div>
                  <div className="text-slate text-xs">{r.started_at ? new Date(r.started_at).toLocaleString() : ""}</div>
                </td>
                <td className="px-4 py-3"><Badge status={r.state === "completed" ? "green" : r.state === "recording" ? "running" : "failed"}>{r.state}</Badge></td>
                <td className="px-4 py-3 text-slate">{fmtDur(r.duration_s)}</td>
                <td className="px-4 py-3 text-slate">{fmtSize(r.size_bytes)}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => download(r)} disabled={r.state === "recording"}>↓</Button>
                    <Button variant="danger" onClick={() => api.del(`/recordings/${r.id}`).then(() => recs.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {recs.data?.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

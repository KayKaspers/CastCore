import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Panel } from "../components/ui";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { Backup } from "../lib/types";
import { useAsync } from "../lib/useAsync";

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function BackupPage() {
  const { t } = useTranslation();
  const backups = useAsync<Backup[]>(() => api.get("/backups"), []);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const create = async () => {
    setError(null);
    setBusy(true);
    try {
      await api.post("/backups");
      backups.reload();
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    } finally {
      setBusy(false);
    }
  };

  const download = async (b: Backup) => {
    const token = useAuthStore.getState().accessToken;
    const res = await fetch(`/api/v1/backups/${b.id}/download`, {
      headers: { authorization: `Bearer ${token}` },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = b.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const restore = async (b: Backup) => {
    if (!window.confirm(t("backup.restoreConfirm", { name: b.filename }))) return;
    setError(null);
    try {
      await api.post(`/backups/${b.id}/restore?confirm=true`);
      alert(t("backup.restoreDone"));
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    }
  };

  const remove = async (b: Backup) => {
    await api.del(`/backups/${b.id}`);
    backups.reload();
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist">{t("nav.backup")}</h1>
        <Button onClick={create} disabled={busy}>{busy ? t("common.loading") : t("backup.create")}</Button>
      </header>

      <p className="text-sm text-slate">{t("backup.note")}</p>
      {error && <p className="text-danger text-sm">{error}</p>}

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Datei</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(backups.data ?? []).map((b) => (
              <tr key={b.id} className="border-b border-slate/10">
                <td className="px-4 py-3">
                  <div className="text-mist font-mono text-xs">{b.filename}</div>
                  <div className="text-slate text-xs">{new Date(b.created_at).toLocaleString()} · {fmtSize(b.size_bytes)} · {b.kind}</div>
                </td>
                <td className="px-4 py-3"><Badge status={b.status === "completed" ? "green" : "pending"}>{b.status}</Badge></td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => download(b)}>↓</Button>
                    <Button variant="ghost" onClick={() => restore(b)}>{t("backup.restore")}</Button>
                    <Button variant="danger" onClick={() => remove(b)}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {backups.data?.length === 0 && <tr><td colSpan={3} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

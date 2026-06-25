import { useState } from "react";
import { useTranslation } from "react-i18next";

import HelpLink from "../components/HelpLink";
import { Badge, Button, Input, Panel } from "../components/ui";
import { api } from "../lib/api";
import type { AuditEvent } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function AuditPage() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState("");
  const query = filter ? `?action=${encodeURIComponent(filter)}` : "";
  const events = useAsync<AuditEvent[]>(() => api.get(`/audit${query}`), [query]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
        {t("nav.audit")} <HelpLink page="admin-guide/security.md" />
      </h1>
      {events.error && <p className="text-danger text-sm">{events.error}</p>}

      <div className="flex items-center gap-2">
        <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="action filter, z. B. auth.login" />
        <Button variant="ghost" onClick={() => events.reload()}>↻</Button>
      </div>

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Zeit</th>
              <th className="px-4 py-3">Akteur</th>
              <th className="px-4 py-3">Aktion</th>
              <th className="px-4 py-3">Ziel</th>
              <th className="px-4 py-3">IP</th>
            </tr>
          </thead>
          <tbody>
            {(events.data ?? []).map((e) => (
              <tr key={e.id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-slate text-xs whitespace-nowrap">{new Date(e.at).toLocaleString()}</td>
                <td className="px-4 py-3 text-mist">{e.actor ?? "—"}</td>
                <td className="px-4 py-3"><Badge status="pending">{e.action}</Badge></td>
                <td className="px-4 py-3 text-slate text-xs">{e.target_type ? `${e.target_type}` : ""} {e.target_id ? `· ${e.target_id.slice(0, 8)}` : ""}</td>
                <td className="px-4 py-3 text-slate text-xs">{e.ip ?? "—"}</td>
              </tr>
            ))}
            {events.data?.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

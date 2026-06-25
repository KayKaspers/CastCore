import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import HelpLink from "../components/HelpLink";
import { Badge, Panel } from "../components/ui";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";

interface UpdateState {
  current_version: string;
  environment: string;
  deployment: string;
  db_revision: string | null;
  head_revision: string | null;
  up_to_date: boolean;
}

export default function UpdatesPage() {
  const { t } = useTranslation();
  const state = useAsync<UpdateState>(() => api.get("/update/state"), []);
  const s = state.data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
        {t("nav.updates")} <HelpLink page="user-guide/updates.md" />
      </h1>
      {state.error && <p className="text-danger text-sm">{state.error}</p>}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="Version" value={s?.current_version ?? "…"} />
        <Stat label="Environment" value={s?.environment ?? "…"} />
        <Stat label="Deployment" value={s?.deployment ?? "…"} />
        <Stat label="Migrationen" value={s ? (s.up_to_date ? "aktuell" : "ausstehend") : "…"} accent={s?.up_to_date} />
      </div>

      <Panel className="space-y-2 max-w-xl">
        <h2 className="text-mist mb-2">{t("nav.updates")}</h2>
        <Row label="DB-Revision" value={s?.db_revision ?? "—"} />
        <Row label="Head-Revision" value={s?.head_revision ?? "—"} />
        <Row label="Schema aktuell" value={<Badge status={s?.up_to_date ? "green" : "yellow"}>{s?.up_to_date ? "ja" : "nein"}</Badge>} />
        {s && !s.up_to_date && (
          <p className="text-warning text-xs pt-2">
            Die Datenbank ist nicht auf dem neuesten Stand. Beim nächsten Start werden Migrationen
            automatisch angewendet (Docker), oder führe <code className="text-signal-cyan">update.sh</code> aus.
          </p>
        )}
      </Panel>

      <Panel className="max-w-xl">
        <h2 className="text-mist mb-2">{t("updates.howto")}</h2>
        <Link to="/docs?p=de/user-guide/updates.md" className="text-signal-cyan text-sm hover:underline">→ {t("updates.guide")}</Link>
      </Panel>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <Panel className="!p-4">
      <div className="text-xs uppercase tracking-wide text-slate">{label}</div>
      <div className={`text-xl font-semibold mt-1 ${accent ? "text-core-green" : "text-mist"}`}>{value}</div>
    </Panel>
  );
}

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-slate/10 pb-2 text-sm">
      <span className="text-slate">{label}</span>
      <span className="text-mist font-mono text-xs">{value}</span>
    </div>
  );
}

import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Panel } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { SetupStatus, SystemCheckResult } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function SetupWizardPage() {
  const { t } = useTranslation();
  const setup = useAsync<SetupStatus>(() => api.get("/setup/state"), []);
  const [check, setCheck] = useState<SystemCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async (fn: () => Promise<unknown>) => {
    setError(null);
    setBusy(true);
    try {
      await fn();
      setup.reload();
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    } finally {
      setBusy(false);
    }
  };

  const runSyscheck = async () => {
    setError(null);
    try {
      const result = await api.post<SystemCheckResult>("/setup/syscheck");
      setCheck(result);
    } catch (e) {
      if (e instanceof ApiException) setError(e.localized);
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-mist">{t("setup.title")}</h1>
        {setup.data && (
          <p className="text-sm mt-1">
            {setup.data.completed ? <Badge status="green">{t("health.green")}</Badge> : <Badge status="pending" />}
          </p>
        )}
      </header>

      {error && <p className="text-danger text-sm">{error}</p>}

      <Panel>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-mist">Steps</h2>
          <Button variant="ghost" onClick={runSyscheck}>{t("setup.step.syscheck")}</Button>
        </div>
        <ul className="space-y-2">
          {(setup.data?.steps ?? []).map((s) => (
            <li key={s.step} className="flex items-center justify-between border-b border-slate/10 pb-2">
              <span className="text-mist text-sm">{t(`setup.step.${s.step}`, { defaultValue: s.step })}</span>
              <div className="flex items-center gap-3">
                <Badge status={s.status} />
                {s.status === "pending" && s.step !== "complete" && (
                  <Button variant="ghost" disabled={busy}
                    onClick={() => run(() => api.post(`/setup/step/${s.step}?status=done`))}>
                    {t("common.save")}
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
        {setup.data && !setup.data.completed && (
          <Button className="mt-4" disabled={busy} onClick={() => run(() => api.post("/setup/complete"))}>
            {t("setup.step.complete")}
          </Button>
        )}
      </Panel>

      {check && (
        <Panel>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-mist">{t("setup.step.syscheck")}</h2>
            <Badge status={check.level} />
          </div>
          <ul className="space-y-2 text-sm">
            {check.items.map((i) => (
              <li key={i.key} className="flex items-center justify-between border-b border-slate/10 pb-2">
                <span className="text-slate">{i.key}</span>
                <span className="flex items-center gap-2">
                  <span className="text-mist/70 text-xs">{i.detail}</span>
                  <Badge status={i.ok ? "green" : "red"} />
                </span>
              </li>
            ))}
          </ul>
        </Panel>
      )}
    </div>
  );
}

import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import logo from "../assets/castcore-logo-stacked-dark.svg";
import { Button, Field, Input, Panel } from "../components/ui";
import i18n from "../i18n";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [firstRun, setFirstRun] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (firstRun) {
        await api.post("/setup/admin", { username, password, language: i18n.language });
      }
      await login(username, password);
      navigate("/");
    } catch (err) {
      if (err instanceof ApiException) setError(err.localized);
      else setError(i18n.t(`error.${(err as Error).message}`, { defaultValue: (err as Error).message }));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <img src={logo} alt="CastCore" className="h-20 mx-auto mb-6" />
        <p className="text-center text-core-green text-sm mb-6">{t("app.claim")}</p>
        <Panel>
          <h1 className="text-lg text-mist mb-4">
            {firstRun ? t("setup.step.admin") : t("auth.login")}
          </h1>
          <form onSubmit={onSubmit} className="space-y-4">
            <Field label={t("auth.username")}>
              <Input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
            </Field>
            <Field label={t("auth.password")}>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </Field>
            {error && <p className="text-danger text-sm">{error}</p>}
            <Button type="submit" disabled={busy} className="w-full">
              {busy ? t("common.loading") : firstRun ? t("common.create") : t("auth.login")}
            </Button>
          </form>
          <button
            onClick={() => { setFirstRun((v) => !v); setError(null); }}
            className="mt-4 text-xs text-slate hover:text-core-green w-full text-center"
          >
            {firstRun ? t("auth.login") : t("setup.firstRun")}
          </button>
        </Panel>
      </div>
    </div>
  );
}

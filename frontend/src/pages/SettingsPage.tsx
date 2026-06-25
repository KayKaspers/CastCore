import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import HelpLink from "../components/HelpLink";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { setLanguage } from "../i18n";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import { useAsync } from "../lib/useAsync";

interface GlobalSettings {
  instance_name?: string;
  default_language?: string;
}

export default function SettingsPage() {
  const { t, i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const isAdmin = useAuthStore((s) => s.hasRole)("admin");
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const changeLanguage = async (lang: "de" | "en") => {
    setError(null); setMsg(null);
    try {
      await api.patch("/settings/me", { language: lang });
      setLanguage(lang); // immediate UI switch + localStorage
      setMsg(t("settings.saved"));
    } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
        {t("nav.settings")} <HelpLink page="user-guide/settings.md" />
      </h1>
      {error && <p className="text-danger text-sm">{error}</p>}
      {msg && <p className="text-core-green text-sm">{msg}</p>}

      <Panel className="space-y-4 max-w-xl">
        <h2 className="text-mist">{t("settings.profile")}</h2>
        <div className="text-sm text-slate">
          {user?.username} · {user?.roles.map((r) => <Badge key={r} status="pending">{r}</Badge>)}
        </div>
        <Field label={t("common.language")}>
          <Select value={i18n.language === "en" ? "en" : "de"} onChange={(e) => changeLanguage(e.target.value as "de" | "en")}>
            <option value="de">Deutsch</option>
            <option value="en">English</option>
          </Select>
        </Field>
        <p className="text-xs text-slate">{t("settings.languageNote")}</p>
      </Panel>

      {isAdmin && <InstanceSettings onError={onErr} onSaved={() => setMsg(t("settings.saved"))} />}

      <Panel className="max-w-xl">
        <h2 className="text-mist mb-2">{t("settings.setup")}</h2>
        <Link to="/setup" className="text-signal-cyan text-sm hover:underline">→ {t("setup.title")}</Link>
      </Panel>
    </div>
  );
}

function InstanceSettings({ onError, onSaved }: { onError: (e: unknown) => void; onSaved: () => void }) {
  const { t } = useTranslation();
  const current = useAsync<GlobalSettings>(() => api.get("/settings"), []);
  const [name, setName] = useState<string | null>(null);
  const [defLang, setDefLang] = useState<string | null>(null);

  const nameVal = name ?? current.data?.instance_name ?? "";
  const langVal = defLang ?? current.data?.default_language ?? "de";

  const save = async () => {
    try {
      await api.patch("/settings", { instance_name: nameVal, default_language: langVal });
      current.reload();
      onSaved();
    } catch (e) { onError(e); }
  };

  return (
    <Panel className="space-y-4 max-w-xl">
      <h2 className="text-mist">{t("settings.instance")}</h2>
      <Field label={t("settings.instanceName")}>
        <Input value={nameVal} onChange={(e) => setName(e.target.value)} placeholder="CastCore" />
      </Field>
      <Field label={t("settings.defaultLanguage")}>
        <Select value={langVal} onChange={(e) => setDefLang(e.target.value)}>
          <option value="de">Deutsch</option>
          <option value="en">English</option>
        </Select>
      </Field>
      <Button onClick={save}>{t("common.save")}</Button>
    </Panel>
  );
}

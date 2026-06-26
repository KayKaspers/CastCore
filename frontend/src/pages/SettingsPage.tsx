import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import HelpLink from "../components/HelpLink";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { setLanguage } from "../i18n";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { ApiToken, ApiTokenCreated, AuthSession } from "../lib/types";
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

      <TwoFactorSettings onError={onErr} onSaved={(m) => setMsg(m)} />

      <ApiTokensSettings onError={onErr} />

      <SessionsSettings onError={onErr} />

      {isAdmin && <InstanceSettings onError={onErr} onSaved={() => setMsg(t("settings.saved"))} />}

      <Panel className="max-w-xl">
        <h2 className="text-mist mb-2">{t("settings.setup")}</h2>
        <Link to="/setup" className="text-signal-cyan text-sm hover:underline">→ {t("setup.title")}</Link>
      </Panel>
    </div>
  );
}

interface TotpSetup {
  secret: string;
  otpauth_uri: string;
}

function TwoFactorSettings({
  onError,
  onSaved,
}: {
  onError: (e: unknown) => void;
  onSaved: (msg: string) => void;
}) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const enabled = !!user?.totp_enabled;

  const [setup, setSetup] = useState<TotpSetup | null>(null);
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);

  const begin = async () => {
    setBusy(true);
    try {
      setSetup(await api.post<TotpSetup>("/auth/2fa/setup"));
      setCode("");
    } catch (e) { onError(e); } finally { setBusy(false); }
  };

  const confirm = async () => {
    setBusy(true);
    try {
      await api.post("/auth/2fa/verify", { code });
      updateUser({ totp_enabled: true });
      setSetup(null);
      setCode("");
      onSaved(t("settings.twofa.enabledMsg"));
    } catch (e) { onError(e); } finally { setBusy(false); }
  };

  const disable = async () => {
    setBusy(true);
    try {
      await api.post("/auth/2fa/disable", { code });
      updateUser({ totp_enabled: false });
      setCode("");
      onSaved(t("settings.twofa.disabledMsg"));
    } catch (e) { onError(e); } finally { setBusy(false); }
  };

  return (
    <Panel className="space-y-4 max-w-xl">
      <h2 className="text-mist flex items-center gap-2">
        {t("settings.twofa.title")}
        <Badge status={enabled ? "running" : "stopped"}>
          {enabled ? t("settings.twofa.on") : t("settings.twofa.off")}
        </Badge>
      </h2>
      <p className="text-xs text-slate">{t("settings.twofa.intro")}</p>

      {!enabled && !setup && (
        <Button onClick={begin} disabled={busy}>{t("settings.twofa.enable")}</Button>
      )}

      {!enabled && setup && (
        <div className="space-y-3">
          <p className="text-sm text-slate">{t("settings.twofa.scanHint")}</p>
          <div className="text-xs text-slate">
            {t("settings.twofa.manualKey")}:
            <code className="ml-2 text-signal-cyan break-all">{setup.secret}</code>
          </div>
          <a href={setup.otpauth_uri} className="text-signal-cyan text-xs hover:underline break-all">
            {setup.otpauth_uri}
          </a>
          <Field label={t("auth.totpCode")} hint={t("auth.totpHint")}>
            <Input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" placeholder="123456" />
          </Field>
          <div className="flex gap-2">
            <Button onClick={confirm} disabled={busy || !code}>{t("settings.twofa.activate")}</Button>
            <Button variant="ghost" onClick={() => { setSetup(null); setCode(""); }} disabled={busy}>
              {t("common.cancel")}
            </Button>
          </div>
        </div>
      )}

      {enabled && (
        <div className="space-y-3">
          <Field label={t("auth.totpCode")} hint={t("settings.twofa.disableHint")}>
            <Input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" placeholder="123456" />
          </Field>
          <Button variant="danger" onClick={disable} disabled={busy || !code}>
            {t("settings.twofa.disable")}
          </Button>
        </div>
      )}
    </Panel>
  );
}

function ApiTokensSettings({ onError }: { onError: (e: unknown) => void }) {
  const { t, i18n } = useTranslation();
  const tokens = useAsync<ApiToken[]>(() => api.get("/tokens"), []);
  const [name, setName] = useState("");
  const [days, setDays] = useState("");
  const [created, setCreated] = useState<ApiTokenCreated | null>(null);
  const [busy, setBusy] = useState(false);

  const fmt = (s: string | null) =>
    s ? new Date(s).toLocaleString(i18n.language) : "—";

  const create = async () => {
    if (!name.trim()) return;
    setBusy(true);
    try {
      const body: Record<string, unknown> = { name: name.trim() };
      if (days) body.expires_in_days = Number(days);
      setCreated(await api.post<ApiTokenCreated>("/tokens", body));
      setName(""); setDays("");
      tokens.reload();
    } catch (e) { onError(e); } finally { setBusy(false); }
  };

  const revoke = async (id: string) => {
    if (!window.confirm(t("settings.tokens.revokeConfirm"))) return;
    try { await api.del(`/tokens/${id}`); tokens.reload(); } catch (e) { onError(e); }
  };

  return (
    <Panel className="space-y-4 max-w-xl">
      <h2 className="text-mist">{t("settings.tokens.title")}</h2>
      <p className="text-xs text-slate">{t("settings.tokens.intro")}</p>

      {created && (
        <div className="rounded-md border border-core-green/40 bg-core-green/10 p-3 space-y-2">
          <p className="text-xs text-core-green">{t("settings.tokens.created")}</p>
          <code className="block text-sm text-mist break-all">{created.token}</code>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => navigator.clipboard?.writeText(created.token)}>
              {t("settings.tokens.copy")}
            </Button>
            <Button variant="ghost" onClick={() => setCreated(null)}>{t("common.cancel")}</Button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 items-end">
        <Field label={t("settings.tokens.name")}>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="ci-bot" />
        </Field>
        <Field label={t("settings.tokens.expiresDays")}>
          <Input value={days} onChange={(e) => setDays(e.target.value)} inputMode="numeric" placeholder="∞" />
        </Field>
        <Button onClick={create} disabled={busy || !name.trim()}>{t("common.create")}</Button>
      </div>

      <div className="space-y-2">
        {(tokens.data ?? []).map((tk) => (
          <div key={tk.id} className="flex items-center justify-between border-b border-slate/10 pb-2">
            <div>
              <div className="text-sm text-mist">{tk.name}</div>
              <div className="text-xs text-slate">
                {t("settings.tokens.lastUsed")}: {fmt(tk.last_used_at)} · {t("settings.tokens.expires")}: {fmt(tk.expires_at)}
              </div>
            </div>
            <Button variant="danger" onClick={() => revoke(tk.id)}>{t("settings.tokens.revoke")}</Button>
          </div>
        ))}
        {tokens.data?.length === 0 && <p className="text-xs text-slate">{t("settings.tokens.none")}</p>}
      </div>
    </Panel>
  );
}

function SessionsSettings({ onError }: { onError: (e: unknown) => void }) {
  const { t, i18n } = useTranslation();
  const sessions = useAsync<AuthSession[]>(() => api.get("/auth/sessions"), []);
  const fmt = (s: string) => new Date(s).toLocaleString(i18n.language);
  const others = (sessions.data ?? []).filter((s) => !s.current).length;

  const revoke = async (id: string) => {
    try { await api.del(`/auth/sessions/${id}`); sessions.reload(); } catch (e) { onError(e); }
  };

  const revokeOthers = async () => {
    if (!window.confirm(t("settings.sessions.revokeOthersConfirm"))) return;
    try { await api.post("/auth/sessions/revoke-others"); sessions.reload(); } catch (e) { onError(e); }
  };

  return (
    <Panel className="space-y-4 max-w-xl">
      <h2 className="text-mist">{t("settings.sessions.title")}</h2>
      <p className="text-xs text-slate">{t("settings.sessions.intro")}</p>

      <div className="space-y-2">
        {(sessions.data ?? []).map((s) => (
          <div key={s.id} className="flex items-center justify-between border-b border-slate/10 pb-2">
            <div>
              <div className="text-sm text-mist flex items-center gap-2">
                {s.user_agent || t("settings.sessions.unknownDevice")}
                {s.current && <Badge status="running">{t("settings.sessions.current")}</Badge>}
              </div>
              <div className="text-xs text-slate">
                {s.ip ?? "—"} · {t("settings.sessions.since")}: {fmt(s.created_at)}
              </div>
            </div>
            {!s.current && (
              <Button variant="danger" onClick={() => revoke(s.id)}>{t("settings.sessions.revoke")}</Button>
            )}
          </div>
        ))}
        {sessions.data?.length === 0 && <p className="text-xs text-slate">—</p>}
      </div>

      {others > 0 && (
        <Button variant="ghost" onClick={revokeOthers}>{t("settings.sessions.revokeOthers")}</Button>
      )}
    </Panel>
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

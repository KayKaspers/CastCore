import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import HelpLink from "../components/HelpLink";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { ManagedUser } from "../lib/types";
import { useAsync } from "../lib/useAsync";

const ROLES = ["admin", "operator", "viewer"];

export default function UsersPage() {
  const { t } = useTranslation();
  const users = useAsync<ManagedUser[]>(() => api.get("/users"), []);
  const me = useAuthStore((s) => s.user);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const patch = async (id: string, body: Record<string, unknown>) => {
    setError(null);
    try { await api.patch(`/users/${id}`, body); users.reload(); } catch (e) { onErr(e); }
  };

  const toggleRole = (u: ManagedUser, role: string) => {
    const roles = u.roles.includes(role) ? u.roles.filter((r) => r !== role) : [...u.roles, role];
    if (roles.length === 0) return; // keep at least one role
    patch(u.id, { roles });
  };

  const resetPw = (u: ManagedUser) => {
    const pw = window.prompt(`${t("users.resetPw")} – ${u.username}`);
    if (pw && pw.length >= 8) patch(u.id, { password: pw });
    else if (pw) setError(t("error.validation.failed"));
  };

  const reset2fa = async (u: ManagedUser) => {
    if (!window.confirm(t("users.reset2faConfirm", { user: u.username }))) return;
    setError(null);
    try { await api.post(`/users/${u.id}/2fa/reset`); users.reload(); } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
        {t("nav.users")} <HelpLink page="user-guide/users-roles.md" />
      </h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <NewUser onDone={() => users.reload()} onError={onErr} />

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Benutzer</th>
              <th className="px-4 py-3">Rollen</th>
              <th className="px-4 py-3">Aktiv</th>
              <th className="px-4 py-3">{t("users.col2fa")}</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(users.data ?? []).map((u) => (
              <tr key={u.id} className="border-b border-slate/10">
                <td className="px-4 py-3">
                  <div className="text-mist">{u.username} {u.id === me?.id && <Badge status="pending">du</Badge>}</div>
                  <div className="text-xs text-slate">{u.email ?? "—"} · {u.language}</div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-2">
                    {ROLES.map((r) => (
                      <label key={r} className="flex items-center gap-1 text-xs text-mist">
                        <input type="checkbox" checked={u.roles.includes(r)} onChange={() => toggleRole(u, r)} /> {r}
                      </label>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <input type="checkbox" checked={u.is_active} disabled={u.id === me?.id}
                         onChange={(e) => patch(u.id, { is_active: e.target.checked })} />
                </td>
                <td className="px-4 py-3">
                  <Badge status={u.totp_enabled ? "running" : "stopped"}>
                    {u.totp_enabled ? t("settings.twofa.on") : t("settings.twofa.off")}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    {u.totp_enabled && (
                      <Button variant="ghost" onClick={() => reset2fa(u)}>{t("users.reset2fa")}</Button>
                    )}
                    <Button variant="ghost" onClick={() => resetPw(u)}>{t("users.resetPw")}</Button>
                    <Button variant="danger" disabled={u.id === me?.id}
                            onClick={() => api.del(`/users/${u.id}`).then(() => users.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {users.data?.length === 0 && <tr><td colSpan={5} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function NewUser({ onDone, onError }: { onDone: () => void; onError: (e: unknown) => void }) {
  const { t } = useTranslation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("operator");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/users", { username, password, email: email || null, roles: [role] });
      setUsername(""); setPassword(""); setEmail("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">{t("common.create")}</h2>
      <form onSubmit={submit} className="grid grid-cols-4 gap-3 items-end">
        <Field label={t("auth.username")}><Input value={username} onChange={(e) => setUsername(e.target.value)} required /></Field>
        <Field label={t("auth.password")}><Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} /></Field>
        <Field label="E-Mail"><Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
        <Field label="Rolle">
          <Select value={role} onChange={(e) => setRole(e.target.value)}>
            {ROLES.map((r) => <option key={r}>{r}</option>)}
          </Select>
        </Field>
        <div className="col-span-4"><Button type="submit">{t("common.create")}</Button></div>
      </form>
    </Panel>
  );
}

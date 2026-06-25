import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import AuthImg from "../components/AuthImg";
import HelpLink from "../components/HelpLink";
import { Badge, Button, Panel } from "../components/ui";
import { api } from "../lib/api";
import { useAuthStore } from "../lib/auth";
import type { Asset } from "../lib/types";
import { useAsync } from "../lib/useAsync";

function fmtSize(b: number): string {
  return b < 1024 * 1024 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1024 / 1024).toFixed(1)} MB`;
}

export default function AssetsPage() {
  const { t } = useTranslation();
  const assets = useAsync<Asset[]>(() => api.get("/assets"), []);
  const fileRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const upload = async (file: File) => {
    setError(null);
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const token = useAuthStore.getState().accessToken;
      const res = await fetch("/api/v1/assets", { method: "POST", headers: { authorization: `Bearer ${token}` }, body: fd });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail?.error?.params?.upload ?? "upload failed");
      }
      assets.reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
          {t("nav.assets")} <HelpLink page="user-guide/metadata-thumbnails.md" />
        </h1>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
          />
          <Button onClick={() => fileRef.current?.click()} disabled={busy}>
            {busy ? t("common.loading") : t("assets.upload")}
          </Button>
        </div>
      </header>

      <p className="text-sm text-slate">{t("assets.note")}</p>
      {error && <p className="text-danger text-sm">{t(`error.upload.${error}`, { defaultValue: error })}</p>}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {(assets.data ?? []).map((a) => (
          <Panel key={a.id} className="!p-2 space-y-2">
            <AuthImg assetId={a.id} className="w-full h-32 object-cover rounded-md" alt={a.original_name ?? a.filename} />
            <div className="text-xs text-mist truncate" title={a.original_name ?? a.filename}>{a.original_name ?? a.filename}</div>
            <div className="flex items-center justify-between text-xs text-slate">
              <span>{a.width && a.height ? `${a.width}×${a.height}` : a.mime} · {fmtSize(a.size_bytes)}</span>
              {a.used && <Badge status="green">used</Badge>}
            </div>
            <Button variant="danger" className="w-full" onClick={() => api.del(`/assets/${a.id}`).then(() => assets.reload())}>✕</Button>
          </Panel>
        ))}
        {assets.data?.length === 0 && <p className="text-slate col-span-full text-center py-8">—</p>}
      </div>
    </div>
  );
}

import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { Channel, FFmpegProfile, Playlist } from "../lib/types";
import { useAsync } from "../lib/useAsync";

export default function ChannelsPage() {
  const { t } = useTranslation();
  const channels = useAsync<Channel[]>(() => api.get("/channels"), []);
  const playlists = useAsync<Playlist[]>(() => api.get("/playlists"), []);
  const profiles = useAsync<FFmpegProfile[]>(() => api.get("/ffmpeg-profiles"), []);
  const [error, setError] = useState<string | null>(null);

  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const act = async (id: string, verb: "start" | "stop") => {
    setError(null);
    try { await api.post(`/channels/${id}/${verb}`); channels.reload(); } catch (e) { onErr(e); }
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-mist">{t("nav.channels")}</h1>
        <a href="/api/v1/channels/export.m3u" className="text-xs text-signal-cyan hover:underline" target="_blank" rel="noreferrer">
          M3U-Lineup ↗
        </a>
      </header>
      {error && <p className="text-danger text-sm">{error}</p>}

      <NewChannel playlists={playlists.data ?? []} profiles={profiles.data ?? []} onDone={() => channels.reload()} onError={onErr} />

      <Panel className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="text-slate text-left text-xs uppercase">
            <tr className="border-b border-slate/20">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3">Outputs</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {(channels.data ?? []).map((ch) => (
              <tr key={ch.id} className="border-b border-slate/10">
                <td className="px-4 py-3 text-mist">{ch.name}</td>
                <td className="px-4 py-3"><Badge status={ch.status}>{ch.status}</Badge></td>
                <td className="px-4 py-3 text-xs">
                  <a href={`/api/v1/channels/${ch.id}/hls/index.m3u8`} target="_blank" rel="noreferrer" className="text-signal-cyan hover:underline mr-3">HLS</a>
                  <a href={`/api/v1/channels/${ch.id}/epg.xml`} target="_blank" rel="noreferrer" className="text-signal-cyan hover:underline">EPG</a>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 justify-end">
                    <Button variant="ghost" onClick={() => act(ch.id, "start")}>{t("common.start")}</Button>
                    <Button variant="ghost" onClick={() => act(ch.id, "stop")}>{t("common.stop")}</Button>
                    <Button variant="danger" onClick={() => api.del(`/channels/${ch.id}`).then(() => channels.reload())}>✕</Button>
                  </div>
                </td>
              </tr>
            ))}
            {channels.data?.length === 0 && <tr><td colSpan={4} className="px-4 py-6 text-center text-slate">—</td></tr>}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function NewChannel({ playlists, profiles, onDone, onError }: {
  playlists: Playlist[]; profiles: FFmpegProfile[]; onDone: () => void; onError: (e: unknown) => void;
}) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [playlistId, setPlaylistId] = useState("");
  const [profileId, setProfileId] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/channels", { name, playlist_id: playlistId || null, ffmpeg_profile_id: profileId || null });
      setName("");
      onDone();
    } catch (e) { onError(e); }
  };

  return (
    <Panel>
      <h2 className="text-mist mb-3">{t("common.create")}</h2>
      <form onSubmit={submit} className="grid grid-cols-3 gap-3 items-end">
        <Field label="Name"><Input value={name} onChange={(e) => setName(e.target.value)} required /></Field>
        <Field label={t("nav.playlists")}>
          <Select value={playlistId} onChange={(e) => setPlaylistId(e.target.value)} required>
            <option value="">—</option>
            {playlists.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        </Field>
        <Field label="FFmpeg Profile">
          <Select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
            <option value="">default (libx264)</option>
            {profiles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        </Field>
        <div className="col-span-3"><Button type="submit">{t("common.create")}</Button></div>
      </form>
    </Panel>
  );
}

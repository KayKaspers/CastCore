import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";

import HelpLink from "../components/HelpLink";
import { Badge, Button, Field, Input, Panel, Select } from "../components/ui";
import { api, ApiException } from "../lib/api";
import type { FFmpegProfile } from "../lib/types";
import { useAsync } from "../lib/useAsync";

const VIDEO_CODECS = ["libx264", "libx265", "h264_nvenc", "hevc_nvenc", "h264_qsv", "h264_vaapi", "libvpx-vp9", "libaom-av1"];
const AUDIO_CODECS = ["aac", "libfdk_aac", "libmp3lame", "libopus", "ac3"];
const PRESETS = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"];
const PIXFMTS = ["yuv420p", "yuv422p", "yuv444p", "nv12", "p010le"];

interface Form {
  name: string; copy_mode: boolean;
  vcodec: string; vbitrate: string; width: string; height: string; fps: string;
  preset: string; tune: string; gop: string; pixel_format: string;
  acodec: string; abitrate: string; adisabled: boolean;
  filter: string; expert: string;
}

const EMPTY: Form = {
  name: "", copy_mode: false,
  vcodec: "libx264", vbitrate: "6000k", width: "", height: "", fps: "",
  preset: "veryfast", tune: "", gop: "", pixel_format: "yuv420p",
  acodec: "aac", abitrate: "160k", adisabled: false, filter: "", expert: "",
};

function str(v: unknown): string { return v == null ? "" : String(v); }

function fromProfile(p: FFmpegProfile): Form {
  const v = (p.video ?? {}) as Record<string, unknown>;
  const a = (p.audio ?? {}) as Record<string, unknown>;
  return {
    name: p.name, copy_mode: p.copy_mode,
    vcodec: str(v.codec) || "libx264", vbitrate: str(v.bitrate), width: str(v.width), height: str(v.height),
    fps: str(v.fps), preset: str(v.preset) || "veryfast", tune: str(v.tune), gop: str(v.gop),
    pixel_format: str(v.pixel_format) || "yuv420p",
    acodec: str(a.codec) || "aac", abitrate: str(a.bitrate), adisabled: Boolean(a.disabled),
    filter: str(((p.filters ?? {}) as Record<string, unknown>).complex),
    expert: (p.expert_args ?? []).join(" "),
  };
}

function buildVideo(f: Form): Record<string, unknown> {
  if (f.copy_mode) return {};
  const v: Record<string, unknown> = { codec: f.vcodec };
  if (f.vbitrate) v.bitrate = f.vbitrate;
  if (f.width && f.height) { v.width = Number(f.width); v.height = Number(f.height); }
  if (f.fps) v.fps = Number(f.fps);
  if (f.preset) v.preset = f.preset;
  if (f.tune) v.tune = f.tune;
  if (f.gop) v.gop = Number(f.gop);
  if (f.pixel_format) v.pixel_format = f.pixel_format;
  return v;
}

function buildAudio(f: Form): Record<string, unknown> {
  if (f.copy_mode) return {};
  if (f.adisabled) return { codec: f.acodec, disabled: true };
  const a: Record<string, unknown> = { codec: f.acodec };
  if (f.abitrate) a.bitrate = f.abitrate;
  return a;
}

function payload(f: Form) {
  return {
    name: f.name, copy_mode: f.copy_mode,
    video: buildVideo(f), audio: buildAudio(f),
    filters: f.filter ? { complex: f.filter } : {},
    expert_args: f.expert.split(/\s+/).filter(Boolean),
  };
}

export default function ProfilesPage() {
  const { t } = useTranslation();
  const profiles = useAsync<FFmpegProfile[]>(() => api.get("/ffmpeg-profiles"), []);
  const [form, setForm] = useState<Form>(EMPTY);
  const [editId, setEditId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const set = <K extends keyof Form>(k: K, v: Form[K]) => setForm((p) => ({ ...p, [k]: v }));
  const onErr = (e: unknown) => { if (e instanceof ApiException) setError(e.localized); };

  const edit = (p: FFmpegProfile) => { setEditId(p.id); setForm(fromProfile(p)); setPreview(null); };
  const reset = () => { setEditId(null); setForm(EMPTY); setPreview(null); };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (editId) await api.patch(`/ffmpeg-profiles/${editId}`, payload(form));
      else await api.post("/ffmpeg-profiles", payload(form));
      reset();
      profiles.reload();
    } catch (e) { onErr(e); }
  };

  const doPreview = async () => {
    setError(null);
    try {
      const v = buildVideo(form);
      const res = await api.post<{ preview: string }>("/ffmpeg/preview", {
        inputs: [{ uri: "testsrc=size=1280x720:rate=30", options: { f: "lavfi" } }],
        outputs: [{
          uri: "rtmp://live.example.tv/app/STREAMKEY",
          fmt: "flv",
          video: form.copy_mode ? { codec: "copy" } : v,
          audio: form.copy_mode ? { codec: "copy" } : buildAudio(form),
        }],
      });
      setPreview(res.preview);
    } catch (e) { onErr(e); }
  };

  const gpu = form.vcodec.includes("nvenc") || form.vcodec.includes("qsv") || form.vcodec.includes("vaapi");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-mist flex items-center gap-2">
        FFmpeg-Profile <HelpLink page="reference/ffmpeg-profiles.md" />
      </h1>
      {error && <p className="text-danger text-sm">{error}</p>}

      <Panel>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-mist">{editId ? t("common.edit") : t("common.create")}</h2>
          {editId && <Button variant="ghost" onClick={reset}>{t("common.cancel")}</Button>}
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <Field label="Name"><Input value={form.name} onChange={(e) => set("name", e.target.value)} required /></Field>
            <label className="flex items-end gap-2 text-sm text-mist pb-2">
              <input type="checkbox" checked={form.copy_mode} onChange={(e) => set("copy_mode", e.target.checked)} />
              Stream Copy (kein Re-Encode)
            </label>
          </div>

          {!form.copy_mode && (
            <>
              <div className="text-xs uppercase tracking-wide text-slate">Video</div>
              <div className="grid grid-cols-4 gap-3">
                <Field label="Codec">
                  <Select value={form.vcodec} onChange={(e) => set("vcodec", e.target.value)}>
                    {VIDEO_CODECS.map((c) => <option key={c}>{c}</option>)}
                  </Select>
                </Field>
                <Field label="Bitrate"><Input value={form.vbitrate} onChange={(e) => set("vbitrate", e.target.value)} placeholder="6000k" /></Field>
                <Field label="Breite"><Input type="number" value={form.width} onChange={(e) => set("width", e.target.value)} placeholder="1280" /></Field>
                <Field label="Höhe"><Input type="number" value={form.height} onChange={(e) => set("height", e.target.value)} placeholder="720" /></Field>
                <Field label="FPS"><Input type="number" value={form.fps} onChange={(e) => set("fps", e.target.value)} placeholder="30" /></Field>
                <Field label="Preset">
                  <Select value={form.preset} onChange={(e) => set("preset", e.target.value)}>
                    <option value="">—</option>
                    {PRESETS.map((p) => <option key={p}>{p}</option>)}
                  </Select>
                </Field>
                <Field label="Tune"><Input value={form.tune} onChange={(e) => set("tune", e.target.value)} placeholder="zerolatency" /></Field>
                <Field label="GOP / Keyframe"><Input type="number" value={form.gop} onChange={(e) => set("gop", e.target.value)} placeholder="60" /></Field>
                <Field label="Pixel-Format">
                  <Select value={form.pixel_format} onChange={(e) => set("pixel_format", e.target.value)}>
                    <option value="">—</option>
                    {PIXFMTS.map((p) => <option key={p}>{p}</option>)}
                  </Select>
                </Field>
              </div>
              {gpu && <p className="text-xs text-signal-cyan">GPU-Encoder gewählt – „Preset" gilt encoder-abhängig; auf der Zielmaschine müssen passende Treiber/Geräte (NVENC/QSV/VAAPI) vorhanden sein.</p>}

              <div className="text-xs uppercase tracking-wide text-slate">Audio</div>
              <div className="grid grid-cols-4 gap-3">
                <Field label="Codec">
                  <Select value={form.acodec} disabled={form.adisabled} onChange={(e) => set("acodec", e.target.value)}>
                    {AUDIO_CODECS.map((c) => <option key={c}>{c}</option>)}
                  </Select>
                </Field>
                <Field label="Bitrate"><Input value={form.abitrate} disabled={form.adisabled} onChange={(e) => set("abitrate", e.target.value)} placeholder="160k" /></Field>
                <label className="flex items-end gap-2 text-sm text-mist pb-2">
                  <input type="checkbox" checked={form.adisabled} onChange={(e) => set("adisabled", e.target.checked)} /> Audio deaktivieren
                </label>
              </div>

              <div className="text-xs uppercase tracking-wide text-slate">Erweitert</div>
              <Field label="Filter (filter_complex)"><Input value={form.filter} onChange={(e) => set("filter", e.target.value)} placeholder="scale=1280:720" /></Field>
              <Field label="Experten-Parameter (durch Leerzeichen getrennt)">
                <Input value={form.expert} onChange={(e) => set("expert", e.target.value)} placeholder="-rc cbr -bufsize 12000k" />
              </Field>
            </>
          )}

          <div className="flex items-center gap-2">
            <Button type="submit">{editId ? t("common.save") : t("common.create")}</Button>
            <Button type="button" variant="ghost" onClick={doPreview}>{t("ffmpeg.commandPreview")}</Button>
          </div>
        </form>

        {preview && (
          <pre className="mt-3 text-xs text-signal-cyan whitespace-pre-wrap break-all bg-deep-navy rounded p-3">{preview}</pre>
        )}
      </Panel>

      <Panel className="!p-0 overflow-hidden">
        <ul>
          {(profiles.data ?? []).map((p) => (
            <li key={p.id} className="flex items-center justify-between px-4 py-3 border-b border-slate/10">
              <button className="text-mist text-sm hover:text-core-green text-left" onClick={() => edit(p)}>{p.name}</button>
              <div className="flex items-center gap-3">
                <Badge status={p.copy_mode ? "pending" : "green"}>{p.copy_mode ? "copy" : str((p.video as Record<string, unknown>)?.codec) || "encode"}</Badge>
                <Button variant="ghost" onClick={() => edit(p)}>{t("common.edit")}</Button>
                <Button variant="danger" onClick={() => api.del(`/ffmpeg-profiles/${p.id}`).then(() => profiles.reload())}>✕</Button>
              </div>
            </li>
          ))}
          {profiles.data?.length === 0 && <li className="px-4 py-6 text-center text-slate">—</li>}
        </ul>
      </Panel>
    </div>
  );
}

import { useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";

import { useLogStream } from "../lib/useLogStream";
import HelpLink from "./HelpLink";
import { Badge, Panel } from "./ui";

export default function LogsPanel({
  jobId,
  jobName,
  onClose,
}: {
  jobId: string;
  jobName: string;
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const { lines, connected } = useLogStream(jobId);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  // Most recent health hint (Stream Health Assistant).
  const hint = useMemo(() => {
    for (let i = lines.length - 1; i >= 0; i--) {
      if (lines[i].hint) return lines[i].hint;
    }
    return null;
  }, [lines]);

  return (
    <Panel>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-mist text-sm flex items-center gap-2">
          {t("nav.logs")} · <span className="text-slate">{jobName}</span>
          <Badge status={connected ? "running" : "stopped"}>{connected ? "live" : "off"}</Badge>
        </h2>
        <button className="text-xs text-slate hover:text-mist" onClick={onClose}>✕</button>
      </div>

      {hint && (
        <div className="mb-3 rounded-md border border-warning/40 bg-warning/10 px-3 py-2 text-sm text-warning flex items-center justify-between gap-3">
          <span>{t(`loghint.${hint}`, { defaultValue: t("loghint.generic") })}</span>
          <HelpLink
            page={hint === "source_missing" ? "troubleshooting/smb-problems.md" : "troubleshooting/ffmpeg-errors.md"}
            label={t("help.moreInfo")}
          />
        </div>
      )}

      <div className="bg-deep-navy rounded-md p-3 h-72 overflow-auto font-mono text-xs leading-relaxed">
        {lines.length === 0 && <div className="text-slate">{t("common.loading")}</div>}
        {lines.map((l, i) => (
          <div key={i} className={l.level === "error" ? "text-danger" : "text-mist/80"}>
            {l.line}
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </Panel>
  );
}

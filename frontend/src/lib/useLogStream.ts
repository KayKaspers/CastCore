import { useEffect, useRef, useState } from "react";

import { useAuthStore } from "./auth";

export interface LogLine {
  output_id: string;
  job_id: string;
  ts: number;
  line: string;
  level: "info" | "error";
  hint: string | null;
}

const MAX_LINES = 500;

/** Subscribe to the live FFmpeg log WebSocket for a job. */
export function useLogStream(jobId: string | null) {
  const [lines, setLines] = useState<LogLine[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;
    setLines([]);
    const token = useAuthStore.getState().accessToken;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/api/v1/ws/logs/${jobId}?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (ev) => {
      try {
        const entry = JSON.parse(ev.data) as LogLine;
        setLines((prev) => {
          const next = [...prev, entry];
          return next.length > MAX_LINES ? next.slice(next.length - MAX_LINES) : next;
        });
      } catch {
        /* ignore malformed frame */
      }
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [jobId]);

  return { lines, connected };
}

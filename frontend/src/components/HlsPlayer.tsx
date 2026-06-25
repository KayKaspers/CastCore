import Hls from "hls.js";
import { useEffect, useRef, useState } from "react";

/**
 * Plays an HLS (.m3u8) stream in the browser. Uses native HLS on Safari and hls.js
 * elsewhere. The CastCore channel HLS endpoints are public, so no auth header is needed.
 */
export default function HlsPlayer({ src, className }: { src: string; className?: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    setError(null);
    let hls: Hls | null = null;

    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src; // Safari / iOS native HLS
    } else if (Hls.isSupported()) {
      hls = new Hls({ liveSyncDurationCount: 3, lowLatencyMode: true });
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.ERROR, (_e, data) => {
        if (data.fatal) setError("stream nicht abspielbar – läuft der Channel?");
      });
    } else {
      setError("HLS wird von diesem Browser nicht unterstützt.");
    }

    return () => { if (hls) hls.destroy(); };
  }, [src]);

  return (
    <div className={className}>
      <video ref={ref} className="w-full rounded-md bg-black" controls autoPlay muted playsInline />
      {error && <p className="text-warning text-xs mt-1">{error}</p>}
    </div>
  );
}

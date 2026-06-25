import { useEffect, useState } from "react";

import { useAuthStore } from "../lib/auth";

/**
 * Renders an image from an authenticated endpoint by fetching it as a blob with the
 * bearer token (a plain <img src> cannot send the Authorization header).
 */
export default function AuthImg({ assetId, className, alt = "" }: { assetId: string; className?: string; alt?: string }) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    let revoked = false;
    let objectUrl: string | null = null;
    const token = useAuthStore.getState().accessToken;
    fetch(`/api/v1/assets/${assetId}/file`, { headers: { authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.blob() : Promise.reject(r.status)))
      .then((blob) => {
        if (revoked) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch(() => setUrl(null));
    return () => {
      revoked = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [assetId]);

  if (!url) return <div className={`bg-deep-navy ${className ?? ""}`} />;
  return <img src={url} className={className} alt={alt} />;
}

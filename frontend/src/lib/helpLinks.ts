// Maps UI areas to their documentation page (path relative to docs/<lang>/).
// Used by the HelpLink component and the Help navigation.

export const HELP_LINKS: Record<string, string> = {
  dashboard: "user-guide/dashboard.md",
  streams: "user-guide/streams.md",
  "stream-editor": "user-guide/stream-editor.md",
  sources: "user-guide/sources-storage.md",
  "smb": "troubleshooting/smb-problems.md",
  media: "user-guide/media-library.md",
  playlists: "user-guide/playlists.md",
  channels: "user-guide/channels.md",
  platforms: "user-guide/platforms.md",
  metadata: "user-guide/metadata-thumbnails.md",
  recordings: "user-guide/recordings-replay.md",
  monitoring: "user-guide/monitoring.md",
  preflight: "user-guide/preflight-checks.md",
  scheduler: "user-guide/settings.md",
  notifications: "user-guide/settings.md",
  backup: "user-guide/backup-restore.md",
  users: "user-guide/users-roles.md",
  "ffmpeg-errors": "troubleshooting/ffmpeg-errors.md",
  "stream-not-starting": "troubleshooting/stream-not-starting.md",
};

/** Build the in-app docs URL for a docs page in the given language. */
export function docsHref(page: string, lang: string): string {
  const l = lang === "en" ? "en" : "de";
  return `/docs?p=${encodeURIComponent(`${l}/${page}`)}`;
}

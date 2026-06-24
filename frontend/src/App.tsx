import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import logo from "./assets/castcore-logo-horizontal-dark.svg";
import { setLanguage } from "./i18n";

const NAV_KEYS = [
  "dashboard", "streamJobs", "channels", "sources", "mediaLibrary", "playlists",
  "platforms", "assets", "logs", "monitoring", "preflight", "recordings",
  "settings", "users", "backup", "updates"
] as const;

export default function App() {
  const { t, i18n } = useTranslation();
  const [health, setHealth] = useState<string>("…");

  useEffect(() => {
    fetch("/api/v1/health")
      .then((r) => r.json())
      .then((d) => setHealth(`${d.status} · v${d.version}`))
      .catch(() => setHealth("offline"));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate/20">
        <img src={logo} alt="CastCore" className="h-9" />
        <div className="flex items-center gap-3 text-sm">
          <button
            onClick={() => setLanguage("de")}
            className={i18n.language === "de" ? "text-core-green" : "text-slate"}
          >
            DE
          </button>
          <span className="text-slate/40">|</span>
          <button
            onClick={() => setLanguage("en")}
            className={i18n.language === "en" ? "text-core-green" : "text-slate"}
          >
            EN
          </button>
        </div>
      </header>

      <main className="flex-1 px-6 py-10 max-w-5xl mx-auto w-full">
        <h1 className="text-3xl font-semibold text-mist">{t("app.name")}</h1>
        <p className="text-core-green mt-1 font-medium">{t("app.claim")}</p>
        <p className="text-slate mt-1">{t("app.tagline")}</p>

        <div className="cc-panel p-4 mt-8 inline-flex items-center gap-2 text-sm">
          <span className="text-slate">API:</span>
          <span className="text-signal-cyan">{health}</span>
        </div>

        <h2 className="text-mist text-lg mt-10 mb-3">Module</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {NAV_KEYS.map((key) => (
            <div key={key} className="cc-panel px-4 py-3 text-sm text-mist hover:border-core-green/50 transition-colors">
              {t(`nav.${key}`)}
            </div>
          ))}
        </div>

        <p className="text-slate/70 text-xs mt-10">
          Phase 1 scaffold · see docs/ROADMAP.md
        </p>
      </main>
    </div>
  );
}

import { useTranslation } from "react-i18next";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import logo from "../assets/castcore-logo-horizontal-dark.svg";
import icon from "../assets/castcore-icon.svg";
import { setLanguage } from "../i18n";
import { useAuthStore } from "../lib/auth";

const NAV = [
  { to: "/", key: "dashboard", end: true },
  { to: "/streams", key: "streamJobs", end: false },
  { to: "/sources", key: "sources", end: false },
  { to: "/media", key: "mediaLibrary", end: false },
  { to: "/monitoring", key: "monitoring", end: false },
  { to: "/recordings", key: "recordings", end: false },
  { to: "/scheduler", key: "scheduler", end: false },
  { to: "/resources", key: "platforms", end: false },
  { to: "/notifications", key: "notifications", end: false },
  { to: "/backup", key: "backup", end: false },
  { to: "/setup", key: "settings", end: false },
];

export default function Layout() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const onLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-slate/20 bg-panel-navy/40 flex flex-col">
        <div className="px-5 py-4 border-b border-slate/20">
          <img src={logo} alt="CastCore" className="h-7" />
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-md text-sm transition ${
                  isActive ? "bg-core-green/15 text-core-green" : "text-mist hover:bg-slate/10"
                }`
              }
            >
              {t(`nav.${item.key}`)}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-slate/20 space-y-3">
          <div className="flex items-center gap-2 text-sm">
            <button onClick={() => setLanguage("de")} className={i18n.language === "de" ? "text-core-green" : "text-slate"}>DE</button>
            <span className="text-slate/40">|</span>
            <button onClick={() => setLanguage("en")} className={i18n.language === "en" ? "text-core-green" : "text-slate"}>EN</button>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <img src={icon} alt="" className="h-6 w-6" />
              <div className="text-xs">
                <div className="text-mist">{user?.username}</div>
                <div className="text-slate">{user?.roles.join(", ")}</div>
              </div>
            </div>
            <button onClick={onLogout} className="text-xs text-slate hover:text-danger">
              {t("auth.logout")}
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

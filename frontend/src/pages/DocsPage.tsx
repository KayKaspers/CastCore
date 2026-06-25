import { marked } from "marked";
import type { MouseEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useSearchParams } from "react-router-dom";

import { Input } from "../components/ui";

interface NavPage { path: string; title: string }
interface NavSection { section: string; key: string; pages: NavPage[] }
type Nav = Record<string, NavSection[]>;

function stripFrontmatter(md: string): string {
  return md.replace(/^---\n[\s\S]*?\n---\n/, "");
}

export default function DocsPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === "en" ? "en" : "de";
  const [params, setParams] = useSearchParams();
  const [nav, setNav] = useState<Nav | null>(null);
  const [html, setHtml] = useState("");
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const page = params.get("p") || `${lang}/index.md`;

  useEffect(() => {
    fetch("/docs-content/nav.json").then((r) => r.json()).then(setNav).catch(() => setError("nav"));
  }, []);

  // Keep the page in sync with the chosen language (map /de/... <-> /en/...).
  useEffect(() => {
    const [pLang, ...rest] = page.split("/");
    if (pLang !== lang && (pLang === "de" || pLang === "en")) {
      setParams({ p: `${lang}/${rest.join("/")}` }, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    setError(null);
    fetch(`/docs-content/${page}`)
      .then((r) => (r.ok ? r.text() : Promise.reject(r.status)))
      .then((md) => setHtml(marked.parse(stripFrontmatter(md)) as string))
      .catch(() => setError("page"));
  }, [page]);

  const sections = nav?.[lang] ?? [];
  const filtered = useMemo(() => {
    if (!query) return sections;
    const q = query.toLowerCase();
    return sections
      .map((s) => ({ ...s, pages: s.pages.filter((p) => p.title.toLowerCase().includes(q)) }))
      .filter((s) => s.pages.length > 0);
  }, [sections, query]);

  // Intercept clicks on internal /docs/...md links inside the rendered content.
  const onContentClick = (e: MouseEvent) => {
    const a = (e.target as HTMLElement).closest("a");
    if (!a) return;
    const href = a.getAttribute("href") || "";
    const m = href.match(/^\/docs\/((?:de|en)\/.*\.md)$/);
    if (m) {
      e.preventDefault();
      setParams({ p: m[1] });
    }
  };

  const crumbs = page.replace(/\.md$/, "").split("/");

  return (
    <div className="flex gap-6">
      <aside className="w-64 shrink-0">
        <Link to="/" className="text-sm text-slate hover:text-core-green">← {t("docs.backToApp")}</Link>
        <div className="mt-4 mb-3">
          <Input placeholder={t("docs.search")} value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <nav className="space-y-4 text-sm max-h-[70vh] overflow-auto pr-2">
          {filtered.map((s) => (
            <div key={s.key}>
              <div className="text-xs uppercase tracking-wide text-slate mb-1">{s.section}</div>
              <ul className="space-y-0.5">
                {s.pages.map((p) => {
                  const target = `${lang}/${p.path}`;
                  const active = page === target;
                  return (
                    <li key={p.path}>
                      <button
                        onClick={() => setParams({ p: target })}
                        className={`block text-left w-full px-2 py-1 rounded ${active ? "bg-core-green/15 text-core-green" : "text-mist hover:bg-slate/10"}`}
                      >
                        {p.title}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </aside>

      <main className="flex-1 min-w-0">
        <div className="text-xs text-slate mb-4">{crumbs.join(" / ")}</div>
        {error === "page" && <p className="text-danger text-sm">Seite nicht gefunden: {page}</p>}
        {error === "nav" && <p className="text-warning text-sm">Docs-Navigation konnte nicht geladen werden (läuft die App über den Reverse Proxy?).</p>}
        <article
          className="cc-prose max-w-3xl"
          onClick={onContentClick}
          dangerouslySetInnerHTML={{ __html: html }}
        />
        <p className="text-xs text-slate mt-8">
          {t("docs.editHint")} <code>docs/{page}</code>
        </p>
      </main>
    </div>
  );
}

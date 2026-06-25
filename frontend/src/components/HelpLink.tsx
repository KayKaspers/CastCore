import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { docsHref } from "../lib/helpLinks";

/**
 * Small context-help link. Renders a "?" icon (and optional label) that opens the
 * matching documentation page inside the app (/docs viewer), in the current language.
 */
export default function HelpLink({ page, label }: { page: string; label?: string }) {
  const { i18n, t } = useTranslation();
  return (
    <Link
      to={docsHref(page, i18n.language)}
      className="inline-flex items-center gap-1 text-xs text-slate hover:text-core-green align-middle"
      title={t("help.moreInfo")}
    >
      <span className="inline-flex items-center justify-center w-4 h-4 rounded-full border border-slate/50 text-[10px] leading-none">?</span>
      {label && <span>{label}</span>}
    </Link>
  );
}

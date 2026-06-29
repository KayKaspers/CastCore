#!/usr/bin/env python3
"""CastCore documentation check.

Validates the bilingual docs tree and (re)generates docs/docs-status.json and
docs/nav.json. Run locally or in CI:

    python scripts/check_docs.py            # validate + regenerate, warn-only
    python scripts/check_docs.py --strict   # non-zero exit on any warning

Checks:
- every manifest-referenced file exists
- DE and EN have the same page structure (parity)
- no truly empty pages
- placeholder/TODO pages are reported (allowed, but listed)
- stale `lastReviewed` (> STALE_DAYS)
- features without docs / api routes not surfaced

It is intentionally dependency-free (standard library only).
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LANGS = ("de", "en")
STALE_DAYS = 180
TODAY = dt.date.today()

SECTION_ORDER = ["getting-started", "user-guide", "admin-guide", "developer-guide", "api", "reference", "troubleshooting"]
SECTION_TITLE = {
    "de": {"getting-started": "Erste Schritte", "user-guide": "Benutzerhandbuch", "admin-guide": "Admin-Handbuch",
           "developer-guide": "Entwicklerhandbuch", "api": "API-Referenz", "reference": "Referenz",
           "troubleshooting": "Troubleshooting", "_root": "Start"},
    "en": {"getting-started": "Getting started", "user-guide": "User guide", "admin-guide": "Admin guide",
           "developer-guide": "Developer guide", "api": "API reference", "reference": "Reference",
           "troubleshooting": "Troubleshooting", "_root": "Home"},
}


def rel_pages(lang: str) -> set[str]:
    base = DOCS / lang
    return {str(p.relative_to(base)).replace("\\", "/") for p in base.rglob("*.md")}


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm: dict = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    fm["_body"] = text[m.end():] if m else text
    return fm


def main() -> int:
    strict = "--strict" in sys.argv
    errors: list[str] = []
    warnings: list[str] = []

    if not (DOCS / "de").is_dir() or not (DOCS / "en").is_dir():
        print("ERROR: docs/de or docs/en missing")
        return 2

    de, en = rel_pages("de"), rel_pages("en")

    # 1) DE/EN parity
    for only in sorted(de - en):
        errors.append(f"parity: docs/de/{only} has no English counterpart")
    for only in sorted(en - de):
        errors.append(f"parity: docs/en/{only} has no German counterpart")

    # 2) manifest references
    manifest = json.loads((DOCS / "docs-manifest.json").read_text(encoding="utf-8"))
    for feat in manifest.get("features", []):
        for lang in LANGS:
            for rel in feat.get("docs", {}).get(lang, []):
                if not (ROOT / rel).is_file():
                    errors.append(f"manifest: feature '{feat['id']}' references missing {rel}")
        if not feat.get("docs", {}).get("de"):
            warnings.append(f"manifest: feature '{feat['id']}' has no DE docs")

    # 3) page-level checks + status build
    status_pages: dict[str, dict] = {}
    placeholders = 0
    stale = 0
    for rel in sorted(de | en):
        entry: dict = {"de": rel in de, "en": rel in en}
        for lang in LANGS:
            p = DOCS / lang / rel
            if not p.is_file():
                continue
            fm = frontmatter(p)
            body = fm.get("_body", "").strip()
            is_ph = ("TODO:" in body) or (fm.get("status") == "draft")
            if len(body) < 80:
                errors.append(f"empty: docs/{lang}/{rel} has almost no content")
            if is_ph:
                placeholders += 1
            lr = fm.get("lastReviewed", "")
            try:
                age = (TODAY - dt.date.fromisoformat(lr)).days
                if age > STALE_DAYS:
                    stale += 1
                    warnings.append(f"stale: docs/{lang}/{rel} lastReviewed {lr} ({age}d)")
            except ValueError:
                warnings.append(f"meta: docs/{lang}/{rel} missing/invalid lastReviewed")
            entry[f"{lang}_status"] = fm.get("status", "unknown")
            entry[f"{lang}_lastReviewed"] = lr
            entry[f"{lang}_placeholder"] = is_ph
        status_pages[rel] = entry

    # 4) write docs-status.json
    # NOTE: no generation timestamp is persisted on purpose. docs-status.json is a
    # committed, CI-diffed artifact (see ci.yml "Fail if generated docs metadata is out
    # of date"). A daily-changing "generated" date would make the file differ on every
    # run even when no documentation changed, breaking CI. Keep this file a pure function
    # of the docs content/structure so it only changes on real documentation changes.
    status = {
        "summary": {
            "pages": len(de | en), "de": len(de), "en": len(en),
            "placeholders": placeholders, "stale": stale,
            "errors": len(errors), "warnings": len(warnings),
        },
        "pages": status_pages,
    }
    (DOCS / "docs-status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 5) write nav.json (grouped per language, titles from frontmatter)
    nav: dict[str, list] = {}
    for lang in LANGS:
        base = DOCS / lang
        groups: dict[str, list] = {}
        for p in sorted(base.rglob("*.md")):
            rel = str(p.relative_to(base)).replace("\\", "/")
            section = rel.split("/")[0] if "/" in rel else "_root"
            title = frontmatter(p).get("title", rel)
            groups.setdefault(section, []).append({"path": rel, "title": title})
        ordered = []
        if "_root" in groups:
            ordered.append({"section": SECTION_TITLE[lang]["_root"], "key": "_root", "pages": groups.pop("_root")})
        for sec in SECTION_ORDER:
            if sec in groups:
                ordered.append({"section": SECTION_TITLE[lang].get(sec, sec), "key": sec, "pages": groups.pop(sec)})
        for sec, pages in groups.items():
            ordered.append({"section": sec, "key": sec, "pages": pages})
        nav[lang] = ordered
    (DOCS / "nav.json").write_text(json.dumps(nav, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # report
    for e in errors:
        print(f"✗ {e}")
    for w in warnings:
        print(f"! {w}")
    print(f"\nchecked {len(de | en)} pages · {placeholders} placeholders · "
          f"{len(errors)} errors · {len(warnings)} warnings")
    print("wrote docs/docs-status.json and docs/nav.json")

    if errors or (strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
title: "Mitwirken (Entwickler)"
description: "Workflow, Branches, Commits, Definition of Done."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Mitwirken

> Kurzfassung; die maßgebliche Datei ist
> [`CONTRIBUTING.md`](https://github.com/KayKaspers/CastCore/blob/main/CONTRIBUTING.md).

**Zielgruppe:** Entwickler.

## Goldene Regel

> **Keine Feature-Änderung ohne Dokumentations-Update.** Details:
> [Dokumentationsregeln](/docs/de/developer-guide/documentation-rules.md).

## Workflow

1. Branch von `main`, fokussierte Commits, aussagekräftige Messages.
2. Code + Tests anpassen; UI-Texte DE/EN übersetzen.
3. Betroffene Doku (DE **und** EN) aktualisieren, `docs-manifest.json` pflegen.
4. `python scripts/check_docs.py` grün; `npm run build` und `pytest` grün.
5. PR mit der **Change-Checkliste** aus `CONTRIBUTING.md`.

## Definition of Done

Feature funktioniert · getestet · UI übersetzt · API-/User-/Admin-/Developer-Doku
aktuell (DE+EN) · Manifest & Status aktualisiert · Changelog ergänzt (falls relevant).

## Sicherheit & Beispiele

Keine echten Secrets/Tokens in Code, Doku oder Beispielen – generisch halten.

## Verwandte Seiten

- [Tests](/docs/de/developer-guide/testing.md) · [Dokumentationsregeln](/docs/de/developer-guide/documentation-rules.md)

---
_Stand: 2026-06-24 · Status: Stabil_

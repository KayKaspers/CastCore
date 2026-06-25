---
title: "Dokumentationsregeln"
description: "Verbindliche Regel: keine Feature-Änderung ohne Docs-Update."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Dokumentationsregeln

> **Verbindlich für CastCore:** *Keine Feature-Änderung ohne Dokumentations-Update.*

**Zielgruppe:** Entwickler (inkl. KI-Assistenten).

## Die Regel

Wenn **Code, UI, API, Datenmodell, Deployment, Konfiguration, Sicherheit, CLI,
Installation oder Verhalten** geändert wird, ist zu prüfen, ob Dokumentation betroffen
ist. Falls ja, müssen die entsprechenden **deutschen und englischen** Dokumentationsdateien
im selben Schritt aktualisiert werden.

Eine Änderung gilt erst als **vollständig**, wenn die zugehörige Dokumentation aktuell ist.

## Definition of Done

Eine Änderung ist erst fertig, wenn:

- [ ] Feature funktioniert und ist getestet
- [ ] UI-Texte sind übersetzt (DE/EN)
- [ ] API-Dokumentation aktualisiert (falls betroffen)
- [ ] User-Doku **DE** aktualisiert (falls betroffen)
- [ ] User-Doku **EN** aktualisiert (falls betroffen)
- [ ] Admin-/Developer-Doku aktualisiert (falls betroffen)
- [ ] [`docs/docs-manifest.json`](/docs/docs-manifest.json) aktualisiert
- [ ] [`docs/docs-status.json`](/docs/docs-status.json) aktualisiert (via Check-Script)
- [ ] `CHANGELOG.md` aktualisiert (falls relevant)

## Werkzeuge

- **Manifest** `docs/docs-manifest.json`: Feature → Docs-Seiten, UI-Routen, API-Routen,
  Modelle, `lastReviewed`.
- **Status** `docs/docs-status.json`: wird vom Check-Script erzeugt (aktuell/veraltet/fehlt/Platzhalter).
- **Check-Script** `scripts/check_docs.py`: prüft Struktur, DE/EN-Synchronität, leere
  Seiten, TODOs, Manifest-Referenzen, veraltete `lastReviewed`-Einträge.
- **CI** `.github/workflows/docs-check.yml`: führt den Check bei Pull Requests aus.

## DE/EN-Synchronität

Für **jede** Seite unter `docs/de/...` muss die gleiche Seite unter `docs/en/...`
existieren (und umgekehrt). Deutsch ist die gepflegte Hauptsprache; Englisch wird
parallel gehalten. Das Check-Script erzwingt strukturelle Parität.

## Verwandte Seiten

- [Mitwirken](/docs/de/developer-guide/contributing.md)
- `CONTRIBUTING.md` (Projektwurzel)

---
_Stand: 2026-06-24 · Status: Stabil_

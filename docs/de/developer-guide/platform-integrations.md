---
title: "Plattform-Integrationen"
description: "Plattform-/Metadaten-Schicht und Erweiterung."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Plattform-Integrationen

> Wie Plattformen/Metadaten umgesetzt sind und wie man sie erweitert.

**Zielgruppe:** Entwickler.

## Trennung von Transport und Metadaten

- **Transport:** `destinations` (URL + Stream-Key) → FFmpeg-Output.
- **Metadaten:** `platform_metadata` pro Stream-Job & Plattform (Titel/Beschreibung/Tags/
  Thumbnail). Aufgelöst über `metadata_service` mit
  [Platzhaltern](/docs/de/reference/placeholders.md).

## Eine Plattform ergänzen

1. Plattform-Wert (z. B. `kick`) in den Metadaten zulassen (Frontend-Auswahl + ggf.
   Validierung).
2. Optional plattformspezifische Hinweise/Warnungen in `metadata_service.resolve_metadata`
   (z. B. „category empfohlen").
3. Doku in [Plattformen](/docs/de/user-guide/platforms.md) und
   [API: Plattformen](/docs/de/api/platforms.md) ergänzen.

## Geplant (Phase 4)

OAuth-Anbindung (Account verbinden, Refresh-Tokens **verschlüsselt** speichern) und
API-gestütztes Setzen von Titel/Thumbnail.

## Verwandte Seiten

- [API: Plattformen & Metadaten](/docs/de/api/platforms.md) · [Platzhalter](/docs/de/reference/placeholders.md)

---
_Stand: 2026-06-24 · Status: Stabil_

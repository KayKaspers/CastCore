---
title: "Metadaten & Thumbnails"
description: "Plattform-Metadaten und Beschreibungsvorlagen mit Platzhaltern pflegen."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Metadaten & Thumbnails

> Pro Stream-Job und Plattform pflegst du eigene **Metadaten** (Titel, Beschreibung,
> Kategorie, Tags, Sprache, Sichtbarkeit, Thumbnail). Vor dem Start werden sie aufgelöst
> und geprüft.

**Zielgruppe:** Anwender / Operatoren. Aufruf: **Stream-Jobs → Meta**.

## Metadaten bearbeiten

1. Bei einem Job auf **Meta** klicken.
2. **Plattform** wählen (Twitch/YouTube/Kick/Facebook/Custom). Ein ✓ markiert bereits
   gepflegte Plattformen.
3. Felder ausfüllen: **Titel**, **Kategorie**, **Tags**, **Sprache**, **Sichtbarkeit**,
   **Beschreibungsvorlage** und **Thumbnail**.
4. **Speichern**. Mit **„Vorschau auflösen"** siehst du den finalen Text.

## Beschreibungsvorlagen mit Platzhaltern

Titel und Beschreibung dürfen [Platzhalter](/docs/de/reference/placeholders.md) enthalten,
z. B. `{stream_title}`, `{date}`, `{platform}`, `{source_name}`. Beispiel:

```
Live: {stream_title} am {date} um {time} | Quelle: {source_name} | #{platform}
```

## Thumbnails & Asset-Bibliothek

Thumbnails verwaltest du unter **Thumbnails / Assets** (`/assets`):

- **Bild hochladen** – erlaubt sind **PNG, JPEG, WebP, GIF** bis **10 MB**.
- Im Metadaten-Editor wählst du pro Plattform ein hochgeladenes Asset als Thumbnail.

### Sicherheit beim Upload

> 🔐 Uploads werden anhand der **Magic Bytes** (nicht nur der Endung) geprüft, auf die
> Größe begrenzt und unter einem **generierten, sicheren Dateinamen** gespeichert. Der
> Originalname landet nie als Pfad auf der Platte; Assets werden nie ausgeführt.

## Hinweise

> 💡 Die Auflösung zeigt **Warnungen** (z. B. fehlendes Thumbnail oder fehlende
> Kategorie), damit du sie vor dem Start beheben kannst.

## Verwandte Seiten

- [Plattformen](/docs/de/user-guide/platforms.md)
- [Platzhalter](/docs/de/reference/placeholders.md)
- [API: Plattformen & Metadaten](/docs/de/api/platforms.md)

---
_Stand: 2026-06-24 · Status: Stabil_

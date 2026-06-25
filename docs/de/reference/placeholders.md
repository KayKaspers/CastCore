---
title: "Platzhalter (Templates)"
description: "Alle Platzhalter für Beschreibungsvorlagen."
lang: de
audience: "Alle Rollen"
status: stable
lastReviewed: 2026-06-24
---

# Platzhalter (Templates)

> In Plattform-**Titeln** und **Beschreibungsvorlagen** kannst du Platzhalter verwenden.
> Vor dem Streamstart löst CastCore sie auf und zeigt die finale Vorschau.

**Zielgruppe:** Alle, die [Metadaten](/docs/de/user-guide/metadata-thumbnails.md) pflegen.

## Verfügbare Platzhalter

| Platzhalter | Bedeutung | Beispielwert |
| --- | --- | --- |
| `{stream_title}` | Name des Stream-Jobs | `Gaming Night` |
| `{date}` | aktuelles Datum | `2026-06-24` |
| `{time}` | aktuelle Uhrzeit | `20:00` |
| `{platform}` | Zielplattform | `twitch` |
| `{category}` | Kategorie der Metadaten | `Just Chatting` |
| `{tags}` | Tags, kommagetrennt | `live, de` |
| `{source_name}` | Name/Datei der ersten Quelle | `show.mp4` |
| `{server_name}` | Servername (DOMAIN) | `castcore.example.com` |
| `{channel_name}` | Channel-Name (bei Channels) | `Mein Kanal` |

## Beispiel

**Vorlage:**
```
Live: {stream_title} am {date} um {time} | Quelle: {source_name} | #{platform}
```
**Aufgelöst:**
```
Live: Gaming Night am 2026-06-24 um 20:00 | Quelle: show.mp4 | #twitch
```

## Hinweise

> 💡 `{stream_title}` ist immer der **Job-Name**, nicht das plattformspezifische
> Titel-Template – so kannst du im Titel selbst `{stream_title}` referenzieren.

## Verwandte Seiten

- [Metadaten & Thumbnails](/docs/de/user-guide/metadata-thumbnails.md)
- [API: Plattformen & Metadaten](/docs/de/api/platforms.md)

---
_Stand: 2026-06-24 · Status: Stabil_

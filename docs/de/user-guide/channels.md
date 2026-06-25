---
title: "Channels (lineares Playout)"
description: "24/7-Channels aus Playlists mit HLS-Output, EPG und M3U."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Channels (lineares Playout)

> Ein **Channel** spielt eine [Playlist](/docs/de/user-guide/playlists.md) als
> kontinuierlichen 24/7-Kanal ab (FFmpeg concat + Loop) und liefert einen HLS-Output
> sowie EPG- und M3U-Export.

**Zielgruppe:** Anwender / Operatoren. UI-Bereich: **Channels** (`/channels`).

## Schritt für Schritt

1. [Playlist](/docs/de/user-guide/playlists.md) mit streamfähigen Medien anlegen.
2. **Channel erstellen**: Name, Playlist, optional FFmpeg-Profil und **Fallback-Video**.
3. **Start** klicken. Der Status wird live abgeglichen (`running`/`stopped`/`failed`).
4. Über die Spalte **Outputs** die Links öffnen:
   - **HLS**: `/api/v1/channels/<id>/hls/index.m3u8`
   - **EPG** (XMLTV): `/api/v1/channels/<id>/epg.xml`
   - **M3U-Lineup** (alle Channels): `/api/v1/channels/export.m3u`

## Fallback & robustes Playout

- Beim Start werden **nicht mehr vorhandene Dateien übersprungen** – eine fehlende Datei
  stoppt den Channel nicht.
- Ist keine Playlist-Datei spielbar und ein **Fallback-Video** gesetzt, läuft dieses in
  Schleife. Ohne beides bricht der Start mit klarer Meldung ab.

## EPG & M3U

- **EPG/XMLTV** wird aus den Item-Dauern als Sendeplan erzeugt (now+next).
- **M3U** liefert eine Senderliste für IPTV-Player.

## Hinweise

> ⚠️ Die HLS-/EPG-/M3U-Endpunkte sind im MVP **ohne Authentifizierung** erreichbar
> (für Player). In Produktion über den Reverse Proxy absichern bzw. signierte URLs nutzen.

## Verwandte Seiten

- [Playlists](/docs/de/user-guide/playlists.md)
- [Medienbibliothek](/docs/de/user-guide/media-library.md)
- [Glossar: HLS, EPG, M3U](/docs/de/reference/glossary.md)

---
_Stand: 2026-06-24 · Status: Stabil_

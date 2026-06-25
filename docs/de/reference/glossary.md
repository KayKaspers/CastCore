---
title: "Glossar"
description: "Zweisprachiges Glossar der Streaming-Begriffe."
lang: de
audience: "Alle Rollen"
status: stable
lastReviewed: 2026-06-24
---

# Glossar

> Kurzdefinitionen der wichtigsten Begriffe in CastCore. Englische Entsprechung siehe
> [`/docs/en/reference/glossary.md`](/docs/en/reference/glossary.md).

| Begriff | Bedeutung |
| --- | --- |
| **FFmpeg** | Werkzeug zum Aufnehmen, Konvertieren und Streamen von Audio/Video. |
| **ffprobe** | Analysiert Mediendateien (Codec, Auflösung, Dauer, Bitrate). |
| **RTMP** | Real-Time Messaging Protocol – verbreitetes Ingest-Protokoll (Twitch, YouTube). |
| **RTSP** | Streaming-Protokoll, oft bei IP-Kameras. |
| **HLS** | HTTP Live Streaming – segmentiertes Streaming über HTTP (`.m3u8` + `.ts`). |
| **LL-HLS** | Low-Latency-HLS – HLS mit reduzierter Latenz. |
| **SRT** | Secure Reliable Transport – verlustarmes Transportprotokoll. |
| **WebRTC** | Echtzeit-Kommunikation im Browser, sehr niedrige Latenz. |
| **Transcoding** | Neukodierung von Audio/Video (Codec/Bitrate/Auflösung ändern). |
| **Remuxing** | Umpacken in einen anderen Container ohne Neukodierung. |
| **Bitrate** | Datenrate pro Sekunde (z. B. 6000 kbit/s). |
| **Framerate** | Bilder pro Sekunde (FPS). |
| **GOP / Keyframe** | Gruppe von Bildern bzw. vollständiges Einzelbild; bestimmt Segmentierung/Latenz. |
| **Codec** | Kodierverfahren (z. B. H.264/libx264, AAC). |
| **Container / Muxer** | Dateiformat, das Streams bündelt (MP4, MPEG-TS). |
| **Preset / Tune** | x264-Geschwindigkeits-/Qualitätsprofil bzw. Feinabstimmung. |
| **Stream Copy** | Durchreichen ohne Neukodierung (`-c copy`). |
| **Input / Output / Destination** | Eingabequelle / Ausgang / konkretes Ziel (URL+Key). |
| **Platform** | Zielplattform (Twitch, YouTube, Kick, eigener RTMP …). |
| **Storage Source / Mount** | Quelle (lokal/SMB/NFS/Cloud) bzw. deren Einbindung. |
| **SMB / NFS / WebDAV / rclone** | Protokolle/Werkzeuge für Netzwerk- und Cloud-Speicher. |
| **OAuth** | Autorisierungsverfahren für Plattform-Konten. |
| **Stream Key** | Geheimer Schlüssel zur Veröffentlichung auf einer Plattform. |
| **Preflight Check** | Startklar-Prüfung vor dem Streamstart (🟢/🟡/🔴). |
| **Health Score** | Bewertung des Stream-Zustands aus Live-Metriken. |
| **Channel** | Linearer 24/7-Kanal aus einer Playlist. |
| **Playlist** | Geordnete/zufällige Liste von Medien. |
| **EPG / XMLTV** | Elektronischer Programmführer bzw. dessen XML-Format. |
| **M3U** | Playlist-/Senderlisten-Format für IPTV-Player. |

## Verwandte Seiten

- [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)
- [Was ist CastCore?](/docs/de/getting-started/overview.md)

---
_Stand: 2026-06-24 · Status: Stabil_

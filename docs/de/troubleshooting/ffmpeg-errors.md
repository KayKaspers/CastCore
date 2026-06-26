---
title: "FFmpeg-Fehler"
description: "Häufige FFmpeg-Fehler erkennen und beheben."
lang: de
audience: "Operatoren / Administratoren"
status: stable
lastReviewed: 2026-06-26
---

# FFmpeg-Fehler

> CastCore wertet FFmpeg-Ausgaben aus und zeigt im Live-Log zusätzlich einen
> **Klartext-Hinweis**. Diese Seite erklärt die häufigsten Fälle.

**Zielgruppe:** Operatoren / Administratoren.

## Symptom: „FFmpeg nicht gefunden"

**Mögliche Ursachen:** FFmpeg ist nicht installiert oder der Pfad in `.env`
(`FFMPEG_PATH`) ist falsch.
**Diagnose:**
```bash
docker compose exec backend ffmpeg -version
```
**Lösung:** In Docker ist FFmpeg im Image enthalten. Nativ: `apt install ffmpeg` und
`FFMPEG_PATH=/usr/bin/ffmpeg` setzen.

## Symptom: „No such file or directory" (Hinweis: *Quelle/Datei nicht gefunden*)

**Ursachen:** Eingabedatei fehlt, Mount verloren, Pfad falsch.
**Diagnose:** Pfad in der [Medienbibliothek](/docs/de/user-guide/media-library.md) prüfen;
bei Netzwerkquellen den [Mount-Status](/docs/de/admin-guide/smb-cifs.md) kontrollieren.
**Lösung:** Quelle neu mounten oder korrekten absoluten Pfad verwenden.

## Symptom: „Invalid data found / could not find codec"

**Ursachen:** Beschädigte Datei oder nicht unterstützter Codec/Container.
**Lösung:** Datei mit ffprobe prüfen, ggf. transcodieren; im Profil **nicht** `copy`
verwenden, sondern neu encodieren (`libx264`/`aac`).

## Symptom: „speed=0.9x" oder darunter

Echtzeit wird nicht gehalten → [Performance](/docs/de/troubleshooting/performance.md).

## Symptom: RTMP rejected / Broken pipe

Plattform weist die Verbindung ab → meist falscher Stream-Key oder URL.
Siehe [Plattform-Fehler](/docs/de/troubleshooting/platform-errors.md).

## „FFmpeg verwundbar" / „Riskanter Codec" (CVE-2026-8461)

- **Systemstatus/Preflight zeigt „FFmpeg verwundbar":** Die installierte FFmpeg-Version ist
  < 8.1.2 und möglicherweise von CVE-2026-8461 (MagicYUV) betroffen. Aktualisiere auf ein
  gepatchtes Build – Wege: [FFmpeg-Anforderungen & Sicherheit](/docs/de/admin-guide/ffmpeg-requirements.md).
- **Preflight ist „rot: Riskanter Codec":** Der Eingang nutzt einen Codec aus der Blocklist
  (z. B. MagicYUV). Bei `BLOCK_RISKY_CODECS=true` (Standard) blockiert CastCore den Start.
  Verwende eine andere Quelle, transkodiere die Datei vorab, oder – nur wenn du der Quelle
  vertraust und FFmpeg gepatcht ist – setze `BLOCK_RISKY_CODECS=false`.
- **Version unbekannt:** CastCore konnte `ffmpeg -version` nicht auswerten. Prüfe `FFMPEG_PATH`
  und dass das Binary erreichbar ist.

## Relevante Logs

```bash
docker compose logs -f process-manager     # spawnt die FFmpeg-Prozesse
```
Im UI: **Stream-Jobs → Live-Logs** (Fehlerzeilen sind rot, mit Hinweis-Banner).

## Verwandte Seiten

- [FFmpeg-Anforderungen & Sicherheit](/docs/de/admin-guide/ffmpeg-requirements.md)
- [FFmpeg Command Builder](/docs/de/developer-guide/ffmpeg-command-builder.md)
- [FFmpeg-Profile](/docs/de/reference/ffmpeg-profiles.md)
- [Glossar](/docs/de/reference/glossary.md)

---
_Stand: 2026-06-26 · Status: Stabil_

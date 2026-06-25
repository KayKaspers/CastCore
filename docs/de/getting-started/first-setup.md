---
title: "Setup-Assistent (Ersteinrichtung)"
description: "Den Setup-Assistenten durchlaufen: Sprache, Admin, Systemcheck."
lang: de
audience: "Einsteiger"
status: stable
lastReviewed: 2026-06-24
---

# Setup-Assistent (Ersteinrichtung)

> Beim ersten Aufruf erkennt CastCore, dass noch kein Administrator existiert, und zeigt
> direkt das Anlege-Formular.

**Zielgruppe:** Einsteiger.
**Voraussetzungen:** Laufende CastCore-Instanz ([Docker](/docs/de/getting-started/installation-docker.md)
oder [nativ](/docs/de/getting-started/installation-native.md)).

## Schritte

1. **`https://<DOMAIN>` öffnen.** Bei `localhost` die Zertifikatswarnung akzeptieren.
2. **Admin anlegen** (Ersteinrichtung): Benutzername + Passwort (mind. 8 Zeichen),
   Sprache (DE/EN). Du wirst danach automatisch angemeldet.
3. **Systemcheck ausführen** (Einstellungen → Setup): prüft FFmpeg/ffprobe, Schreibrechte
   der Datenverzeichnisse und freien Speicher. Ergebnis als Ampel 🟢/🟡/🔴.
4. **Schritte abschließen** und das Setup als „fertig" markieren.

## Die Wizard-Schritte im Überblick

Sprache · Admin-Benutzer · Deployment-Erkennung · FFmpeg-Pfad · ffprobe-Pfad ·
Datenverzeichnis · Medienverzeichnis · Logverzeichnis · Storage-Konzept · Systemcheck · Abschluss.

## Hinweise

> 💡 Es kann nur **ein** Admin per Ersteinrichtung angelegt werden. Existiert bereits
> ein Benutzer, ist die Ersteinrichtung gesperrt (HTTP 409) – melde dich stattdessen an.

> 🔐 Weitere Benutzer und Rollen legst du später unter
> [Benutzer & Rollen](/docs/de/user-guide/users-roles.md) an.

## Bei Problemen

- Login schlägt fehl → [Login funktioniert nicht](/docs/de/troubleshooting/index.md)
- FFmpeg nicht gefunden → [FFmpeg-Fehler](/docs/de/troubleshooting/ffmpeg-errors.md)

## Verwandte Seiten

- [Schnellstart: Erster Stream](/docs/de/getting-started/quickstart.md)
- [Rollen](/docs/de/reference/roles.md)

---
_Stand: 2026-06-24 · Status: Stabil_

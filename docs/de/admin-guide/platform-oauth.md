---
title: "Plattform-OAuth (YouTube/Twitch)"
description: "YouTube-/Twitch-Konten per OAuth verbinden, Tokens sicher speichern."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-26
---

# Plattform-OAuth (YouTube/Twitch)

> Mit OAuth verbindest du echte **Plattform-Konten** mit CastCore. Die Zugriffstokens
> werden **verschlüsselt** gespeichert und ermöglichen es CastCore, Stream-Metadaten in
> deinem Namen zu setzen. Die Integration ist optional und providerbezogen.

**Zielgruppe:** Administratoren.

## Überblick

Eine Plattform ist **aktiviert**, sobald ihre Client-ID konfiguriert ist **und** eine
`PUBLIC_BASE_URL` gesetzt ist. Andernfalls erscheint sie im UI als „nicht konfiguriert".

| Provider | Authorisierung | Standard-Scope |
| --- | --- | --- |
| `youtube` | Google OAuth (`accounts.google.com`) | `…/auth/youtube` |
| `twitch` | Twitch (`id.twitch.tv`) | `channel:manage:broadcast` |

## Einrichten

1. **OAuth-App registrieren** beim Provider (Google Cloud Console bzw. Twitch Developer
   Console) und Client-ID + Secret erzeugen.
2. **Redirect-URI** beim Provider exakt eintragen:
   ```text
   https://<dein-host>/api/v1/oauth/<provider>/callback
   ```
   z. B. `https://stream.example.com/api/v1/oauth/twitch/callback`.
3. In der `.env` setzen:
   ```ini
   PUBLIC_BASE_URL=https://stream.example.com
   TWITCH_CLIENT_ID=…
   TWITCH_CLIENT_SECRET=…
   # und/oder
   YOUTUBE_CLIENT_ID=…
   YOUTUBE_CLIENT_SECRET=…
   ```
4. Backend neu starten. Unter **Plattformen** (`/resources`) erscheint nun **Verbinden**.

## Konto verbinden

1. **Verbinden** klicken – CastCore leitet zum Provider weiter.
2. Beim Provider den Zugriff bestätigen. Der Provider leitet zurück zur Callback-URL.
3. CastCore tauscht den Code gegen Tokens, speichert sie verschlüsselt und zeigt das Konto
   unter **Verbundene Konten**. Trennen ist jederzeit möglich.

## Metadaten-Push (YouTube/Twitch)

Ist ein Konto verbunden, kann CastCore die **Stream-Metadaten direkt auf der Plattform
setzen**. Pro Stream-Job pflegst du die Metadaten (Titel, Beschreibung, Kategorie, Tags,
Sprache, Sichtbarkeit, Thumbnail) und klickst im Metadaten-Panel auf **Metadaten
aktualisieren**.

- **Twitch**: setzt **Titel**, **Kategorie/Spiel** (per Name aufgelöst), **Sprache** und
  **Tags** (`channel:manage:broadcast`).
- **YouTube**: aktualisiert den **aktiven/geplanten Livestream** – **Titel**, **Beschreibung**,
  **Sichtbarkeit**, optional **geplante Startzeit** und **Thumbnail-Upload**
  (`…/auth/youtube`).

Das Ergebnis ist **strukturiert**: `Erfolgreich`, `Mit Warnungen` (z. B. unbekannte Kategorie
oder fehlgeschlagener Thumbnail-Upload – der Rest wird trotzdem gesetzt) oder `Fehler`. Vor
jeder Aktion wird der Token geprüft und bei Bedarf **automatisch erneuert**; Tokens werden nie
geloggt oder zurückgegeben.

| Meldung | Bedeutung |
| --- | --- |
| `platform.not_connected` | Kein verbundenes Konto für die Plattform. |
| `platform.token_expired` | Token abgelaufen und nicht erneuerbar – Konto neu verbinden. |
| `platform.missing_scope` | Fehlende Berechtigungen – Konto mit den nötigen Scopes neu verbinden. |
| `platform.invalid_category` | Twitch-Kategorie nicht gefunden (Warnung). |
| `platform.invalid_broadcast` | Kein aktiver/geplanter YouTube-Livestream. |
| `platform.thumbnail_failed` | YouTube-Thumbnail-Upload fehlgeschlagen (Warnung). |
| `platform.api_error` | Sonstiger Plattform-API-Fehler. |

## Readiness Check (Verbindung testen)

Im Metadaten-Panel prüft **Verbindung testen** pro Plattform die Startklarheit und liefert
einen **Ampelstatus** (🟢 startklar / 🟡 Warnungen / 🔴 nicht startklar). Geprüft werden u. a.:

- **Konto verbunden**, **Token gültig/erneuerbar** (nutzt automatischen Refresh)
- **Berechtigungen/Scopes** vorhanden, **API erreichbar**, **Kontoinformationen** abrufbar
- **Ausgabeziel/URL** gesetzt, **Metadaten** vollständig (Titel)
- **Twitch**: Broadcaster ermittelbar, **Kategorie** gültig (falls gesetzt)
- **YouTube**: aktiver/geplanter **Livestream** vorhanden

🔴 entsteht bei harten Fehlern (kein Konto, ungültiger Token, fehlende Scopes), 🟡 bei
Warnungen (z. B. fehlendes Ausgabeziel, unbekannte Kategorie, kein Broadcast). Tokens werden
dabei **nie** angezeigt oder zurückgegeben.

## Sicherheit

> 🔐 Access- und Refresh-Tokens werden mit **Fernet** verschlüsselt gespeichert
> (`ENCRYPTION_KEY`) und **nie** über die API zurückgegeben (auch nicht im Push-Ergebnis).
> Der OAuth-`state` ist ein kurzlebiges signiertes Token (10 min), das den initiierenden
> Benutzer trägt und CSRF verhindert. Client-Secrets gehören in die `.env`, nicht ins
> Repository.

## Fehlerbehebung

- **Kein „Verbinden"-Button**: `PUBLIC_BASE_URL` und Client-ID gesetzt? Backend neu gestartet?
- **„Verbindung fehlgeschlagen"** nach Rücksprung: Redirect-URI beim Provider muss exakt
  passen (Schema, Host, Pfad). Stimmt das Secret? Ist die Zeit synchron (State-TTL)?
- **`missing_scope` beim Push**: Das Konto wurde ohne die nötigen Scopes verbunden – unter
  **Plattformen** trennen und neu verbinden.
- **`invalid_broadcast` (YouTube)**: Es muss ein **aktiver oder geplanter** Livestream im
  YouTube-Konto existieren, bevor Metadaten gesetzt werden können.
- **Readiness ist 🟡 gelb**: meist `output_missing` (kein Ausgabeziel mit URL) oder
  `metadata_incomplete` (Titel fehlt) – beides nur Warnungen, der Stream lässt sich trotzdem
  starten.

## Verwandte Seiten

- [Plattformen & Metadaten](/docs/de/user-guide/platforms.md)
- [Security Best Practices](/docs/de/admin-guide/security.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-26 · Status: Stabil_

---
title: "Plattform-OAuth (YouTube/Twitch)"
description: "YouTube-/Twitch-Konten per OAuth verbinden, Tokens sicher speichern."
lang: de
audience: "Administratoren"
status: stable
lastReviewed: 2026-06-25
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

## Sicherheit

> 🔐 Access- und Refresh-Tokens werden mit **Fernet** verschlüsselt gespeichert
> (`ENCRYPTION_KEY`) und **nie** über die API zurückgegeben. Der OAuth-`state` ist ein
> kurzlebiges signiertes Token (10 min), das den initiierenden Benutzer trägt und CSRF
> verhindert. Client-Secrets gehören in die `.env`, nicht ins Repository.

## Fehlerbehebung

- **Kein „Verbinden"-Button**: `PUBLIC_BASE_URL` und Client-ID gesetzt? Backend neu gestartet?
- **„Verbindung fehlgeschlagen"** nach Rücksprung: Redirect-URI beim Provider muss exakt
  passen (Schema, Host, Pfad). Stimmt das Secret? Ist die Zeit synchron (State-TTL)?

## Verwandte Seiten

- [Plattformen & Metadaten](/docs/de/user-guide/platforms.md)
- [Security Best Practices](/docs/de/admin-guide/security.md)
- [Umgebungsvariablen](/docs/de/reference/environment-variables.md)

---
_Stand: 2026-06-25 · Status: Stabil_

---
title: "Preflight-Checks"
description: "Vor dem Start prüfen, ob ein Job startklar ist (Ampel) – persistiert als Report."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-29
---

# Preflight-Checks

> Der Preflight-Check prüft **vor** dem Stream-Start, ob ein Job startklar ist, liefert ein
> Ampel-Ergebnis und **speichert einen strukturierten Report**, damit das Ergebnis Neustarts
> übersteht und in Health-Score und Diagnose-Engine einfließt.

**Zielgruppe:** Anwender / Operatoren. Aufruf: **Stream-Jobs → Preflight**.

## Ergebnis-Ampel

- 🟢 **Grün** – startklar.
- 🟡 **Gelb** – Warnungen (z. B. kein Audio), Start möglich.
- 🔴 **Rot** – blockierende Fehler, Start nicht ratsam.
- ⚪ **Grau** – noch keine Prüfung gelaufen (kein Report).

Ein Report trägt zusätzlich ein eigenes **`can_start`**-Flag: es ist nur dann `false`, wenn
ein **blockierender Fehler** vorliegt. Ein roter Report ohne blockierenden Fehler kann den
Start trotzdem erlauben.

## Geprüfte Punkte

Jeder Check hat einen stabilen `code`, eine `category`, eine Stufe (`ok` / `warn` / `error`)
und – bei Fehlern – ein `blocking`-Flag. Checks verweisen auf eine Doku-Seite und enthalten
niemals Secrets.

| Check | Kategorie | Bedeutung |
| --- | --- | --- |
| **input_defined** | input | Mindestens eine Eingabequelle ist definiert. |
| **source_readable** | input | Quelle ist mit ffprobe lesbar. |
| **has_video / has_audio** | input | Eingabe enthält einen Video- / Audiostream. |
| **risky_codec** | security | Eingabe nutzt einen riskanten Codec (z. B. MagicYUV → CVE-2026-8461). |
| **ffmpeg_version** | security | FFmpeg-Version ist bekannt und nicht als verwundbar markiert. |
| **output_enabled** | output | Mindestens ein aktiver Output existiert. |
| **destination_set** | output | Dem Output ist ein Ziel zugewiesen. |
| **stream_key** | output | Stream-Key vorhanden (Plattform-/RTMP-Ziele). |
| **output_writable** | output | Lokaler/Recording-Ausgabepfad ist beschreibbar. |
| **recording_path** | storage | Aufnahmeverzeichnis existiert und ist beschreibbar. |
| **disk_space** | storage | Genug freier Speicher für Aufnahmen. |
| **platform_connected** | platform | Ein verbundenes Konto existiert (Twitch/YouTube). |
| **platform_ready** | platform | Zwischengespeicherte Plattform-Bereitschaft (kein Live-API-Call hier). |
| **metadata_complete** | platform | Plattform-Metadaten (z. B. Titel) sind ausgefüllt. |

## Persistierte Reports

Jeder Preflight-Lauf wird gespeichert. Du kannst die Historie einsehen, ohne die Quelle
erneut zu prüfen:

- **Letzter Report:** das aktuellste Ergebnis eines Jobs.
- **Historie:** die letzten Reports (neueste zuerst).
- **Veraltet (stale):** ein Report, der älter als `PREFLIGHT_REPORT_TTL_SECONDS` ist
  (Standard 600 s), gilt als `stale`. Health-Score und Start-Gate vertrauen nur
  **nicht-veralteten** Reports.

> 🔒 Reports enthalten **niemals** Secrets, Tokens oder Stream-Keys.

## Start-Gate (optional)

Admins können Preflight vor dem Start erzwingen (standardmäßig aus):

| Einstellung | Wirkung |
| --- | --- |
| `PREFLIGHT_REQUIRED_BEFORE_START` | Start wird abgelehnt, solange kein **frischer** (nicht-veralteter) Report existiert. |
| `PREFLIGHT_BLOCK_ON_RED` | Start wird abgelehnt, solange der letzte Report `can_start = false` hat. |
| `PREFLIGHT_REPORT_TTL_SECONDS` | TTL, ab der ein Report als veraltet gilt (Standard 600). |

Blockiert das Gate einen Start, liefert die API `409` mit dem Code `preflight.required` oder
`preflight.blocked`. **Admins** können übersteuern (der Override wird ins Audit-Log
geschrieben); Operatoren müssen das Problem zuerst beheben.

## Schritt für Schritt

1. Auf einem Job **Preflight** klicken.
2. Zuerst rote/blockierende Punkte beheben (Quelle, Output, Stream-Key, Speicherplatz).
3. Bei Grün/Gelb **Start**. Blockiert das Start-Gate, Preflight erneut ausführen (oder als
   Admin übersteuern).

## Dry-Run / Teststream

Neben Preflight gibt es den **Dry-Run**: ein kurzer Test-Encode (~5 Sekunden) mit dem Profil
des Jobs – **ohne** Live-Output und **ohne** Kontakt zum echten Ziel.

- Aufruf: **Stream-Jobs → Dry-Run**.
- Ergebnis: 🟢 ok / 🔴 fehlgeschlagen, gemessene **Encoding-Geschwindigkeit** und **FPS**,
  eine verständliche Meldung und die letzten Log-Zeilen.
- Zweck: prüft, ob die Quelle dekodiert und das Profil enkodiert, und schätzt die Last.

> ⚠️ **Speed < 1.0×** im Dry-Run bedeutet, die Maschine schafft die Echtzeit nicht →
> [Performance](/docs/de/troubleshooting/performance.md).

## Hinweise

> 💡 Preflight nutzt **ffprobe** auf der ersten Quelle – Netzwerk-/Mount-Quellen müssen dafür
> erreichbar sein.

## Verwandte Seiten

- [Stream-Jobs](/docs/de/user-guide/streams.md)
- [Stream startet nicht](/docs/de/troubleshooting/stream-not-starting.md)

---
_Zuletzt geprüft: 2026-06-29 · Status: stable_

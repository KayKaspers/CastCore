---
title: "Preflight-Checks"
description: "Vor dem Start prüfen, ob ein Job startklar ist (Ampel)."
lang: de
audience: "Anwender / Operatoren"
status: stable
lastReviewed: 2026-06-24
---

# Preflight-Checks

> Der Preflight-Check prüft **vor** dem Streamstart, ob ein Job startklar ist, und gibt
> ein Ampel-Ergebnis zurück.

**Zielgruppe:** Anwender / Operatoren. Aufruf: **Stream-Jobs → Preflight**.

## Ergebnis-Ampel

- 🟢 **Grün** – startklar.
- 🟡 **Gelb** – Warnungen (z. B. kein Audio), Start möglich.
- 🔴 **Rot** – blockierende Fehler, Start nicht sinnvoll.

## Geprüfte Punkte (Auswahl)

| Prüfung | Bedeutung |
| --- | --- |
| **source_readable** | Quelle ist mit ffprobe lesbar. |
| **has_video / has_audio** | Eingabe enthält Video- bzw. Audiospur. |
| **outputs / destination** | Mindestens ein aktiver Output mit Ziel. |
| **output_url / stream_key** | Ausgabe-URL gesetzt, Stream-Key vorhanden. |
| **disk_space** | Genug freier Speicher für Aufnahmen. |

## Schritt für Schritt

1. Bei einem Job **Preflight** klicken.
2. Rote Punkte zuerst beheben (Quelle, Output, Stream-Key, Speicher).
3. Bei Grün/Gelb **Start**.

## Hinweise

> 💡 Der Preflight nutzt **ffprobe** auf der ersten Quelle – Netzwerk-/Mount-Quellen
> müssen dafür erreichbar sein.

## Verwandte Seiten

- [Stream-Jobs](/docs/de/user-guide/streams.md)
- [Stream startet nicht](/docs/de/troubleshooting/stream-not-starting.md)

---
_Stand: 2026-06-24 · Status: Stabil_

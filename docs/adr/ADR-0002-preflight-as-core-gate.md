# ADR-0002: Preflight as Core Gate

## Status

Accepted

## Kontext

CastCore benötigt vor Start und Betrieb klare Readiness-Prüfungen.

## Entscheidung

Preflight wird als Core-Gate betrachtet, nicht als optionales Add-on.

## Konsequenzen

- Preflight-Ergebnisse beeinflussen Start-/Betriebsentscheidungen.
- Dokumentation und Releases müssen Preflight berücksichtigen.
- Spätere Module sollen Preflight-kompatibel bleiben.

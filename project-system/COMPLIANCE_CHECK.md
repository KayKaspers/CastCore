# Compliance Check – CastCore

## Summary

CastCore erfüllt bereits viele NDF-Anforderungen für ein reales technisches Projekt.

Besonders stark sind:

- Docker-first
- Preflight
- CI-Erfahrung
- FFmpeg Build-Gates
- gemockte Tests ohne echte ffmpeg-Binary
- dokumentierte Risiken

## Check

| Bereich | Status | Bewertung |
|---|---|---|
| README | warning | NDF-Hinweis später ergänzen |
| Project Brain | pass | durch Baseline vorhanden |
| Roadmap | warning | NDF-kompatibel prüfen |
| ADRs | pass | initiale ADRs vorhanden |
| Prompt Workflow | pass | Nova/Claude Workflow etabliert |
| Quality Gates | pass | Docker/FFmpeg Gates vorhanden |
| Tests | pass | ffmpeg-freie Tests als wichtiges Prinzip |
| CI/CD | pass | letzter bekannter Stand grün |
| Docker | pass | Docker-first |
| Security | warning | vertiefter Review offen |
| Release Notes | warning | Releaseprozess weiter ausarbeiten |
| Lessons Learned | pass | initial dokumentiert |

## Hauptlücken

1. `docs-status.json` Stabilität prüfen.
2. Roadmap und Releaseprozess NDF-kompatibel ausarbeiten.
3. Security Review nachziehen.
4. Health Score nach realem Review aktualisieren.
5. README später um NDF-Abschnitt ergänzen.

## Empfehlung

Nach dieser Baseline zuerst kein Feature bauen, sondern das kleine technische Risiko `docs-status.json` stabilisieren.

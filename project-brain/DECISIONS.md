# Decisions – CastCore

## D-001 – NDF Baseline einführen

CastCore wird als erstes echtes NDF-Referenzprojekt dokumentarisch angebunden.

## D-002 – Keine Codeänderungen in der Baseline

Die NDF-Baseline ergänzt nur Dokumentation, Project System, Project Brain, ADRs und Prompts.

## D-003 – docs-status Stabilität als erstes technisches Work Package

Nach der Baseline wird `docs-status.json` Stabilität priorisiert.

## D-004 – Tests bleiben ffmpeg-frei

Tests sollen weiterhin ffmpeg/ffprobe mocken und keine lokale Binary erfordern.

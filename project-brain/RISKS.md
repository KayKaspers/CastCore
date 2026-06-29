# Risks – CastCore

## R-001 – docs-status.json CI-Diff

### Beschreibung

`docs-status.json` kann durch generierte Datumswerte oder Zeitstempel Änderungen erzeugen, die CI oder Repo-Diffs unnötig instabil machen.

### Wahrscheinlichkeit

Mittel

### Auswirkung

Hoch

### Gegenmaßnahme

Deterministische Generierung oder klare CI-/Dokumentationsregel.

## R-002 – echte FFmpeg-Binary in Tests

### Beschreibung

Tests können fehlschlagen, wenn sie lokale System-Binaries erwarten.

### Wahrscheinlichkeit

Mittel

### Auswirkung

Hoch

### Gegenmaßnahme

Tests weiterhin mocken und keine echte ffmpeg-Binary voraussetzen.

## R-003 – Docker Build-Gate zu spröde

### Beschreibung

Build-Gates können bei externen Image-/Versionsthemen fehlschlagen.

### Wahrscheinlichkeit

Mittel

### Auswirkung

Mittel

### Gegenmaßnahme

Versionen klar pinnen und Fehlermeldungen nachvollziehbar halten.

## R-004 – Dokumentation läuft hinterher

### Beschreibung

CastCore wächst als Suite. Dokumentation und Hilfe können hinter dem Code zurückbleiben.

### Wahrscheinlichkeit

Hoch

### Auswirkung

Mittel

### Gegenmaßnahme

Project Brain, Work Package Queue und Release Checks pflegen.

## R-005 – zu große KI-Arbeitspakete

### Beschreibung

Claude könnte bei zu großen Prompts unübersichtliche Änderungen erzeugen.

### Wahrscheinlichkeit

Mittel

### Auswirkung

Mittel

### Gegenmaßnahme

Kleine Work Packages, klare Grenzen, Rückmeldung an Nova.

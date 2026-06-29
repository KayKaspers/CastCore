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

## R-006 – unsichere Konfigurations-Defaults (SEC-01)

### Beschreibung

`backend/app/core/config.py` enthielt sicherheitsrelevante Fallback-Defaults
(`secret_key="changeme"`, leerer `encryption_key`, `postgres_password="castcore"`) ohne
Fail-Closed-Validierung. Ein produktiver Start mit diesen Werten könnte fälschbare JWTs oder
unsichere Secret-Verarbeitung ermöglichen. Quelle: `CC-WP-006 – Security Baseline Review`.

### Wahrscheinlichkeit

Mittel

### Auswirkung

Hoch

### Gegenmaßnahme

**Mitigiert (CC-WP-007):** Ein `model_validator` in `Settings` bricht bei
`CASTCORE_ENV=production` mit klarer Fehlermeldung ab, wenn `SECRET_KEY`/`ENCRYPTION_KEY`/
`POSTGRES_PASSWORD` leer, ein `changeme`-Platzhalter, ein zu kurzer Secret-Key oder ein
ungültiger Fernet-Key sind. Development/Test behalten die Defaults. Fehlermeldungen nennen nur
Variablennamen, niemals Werte.

### Reststand

Der Guard greift bei Defaults/Platzhaltern, prüft aber keine Passwort-Stärke jenseits der
Länge (z. B. `password123` als `SECRET_KEY` würde akzeptiert). `REDIS_PASSWORD` bleibt im
internen Netz bewusst optional. Vollständige Härtung folgt mit CC-WP-008/009/011.

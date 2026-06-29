# CastCore Release Process

## Zweck

Der Release-Prozess soll CastCore stabil, nachvollziehbar und sicher veröffentlichen.

## Release-Vorbereitung

1. Work Package Queue prüfen.
2. Project Brain aktualisieren.
3. Health Score aktualisieren.
4. Changelog vorbereiten.
5. Release Notes erstellen.
6. CI prüfen.
7. Docker Build-Gates prüfen.
8. Known Issues dokumentieren.

## Release-Typen

- documentation release
- patch release
- feature release
- foundation/core release
- preflight release
- docker/build-gate release

## Release-Gates

Ein Release sollte nicht veröffentlicht werden, wenn:

- CI rot ist
- Docker Build-Gate fehlschlägt
- ffmpeg/ffprobe Prüfung unklar ist
- kritische Preflight-Prüfungen fehlschlagen
- bekannte Risiken nicht dokumentiert sind

## NDF-Regel

Release ist nicht nur ein Tag, sondern ein dokumentierter Zustand.

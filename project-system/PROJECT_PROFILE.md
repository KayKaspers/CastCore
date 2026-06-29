# Project Profile – CastCore

## Kurzbeschreibung

CastCore ist eine self-hosted Medien-, Processing- und Streaming-Suite mit Docker-first-Ansatz.

## Ziel

CastCore soll Medienverarbeitung, FFmpeg-basierte Verarbeitung, Preflight-Prüfungen, Docker-Deployments und kontrollierte Betriebsabläufe in einer professionellen Suite bündeln.

## Zielgruppe

- Self-Hosting-Nutzer
- Content Creator
- technische Betreiber
- Nutzer, die Medienverarbeitung selbst kontrollieren möchten
- spätere Projekte wie mobile/field-orientierte Streaming-Suiten

## Aktueller NDF-Level

```text
Level 3
```

## Ziel-NDF-Level

```text
Level 4
```

## Bekannter Projektstand

- Preflight 2.0 ist implementiert.
- CI war zuletzt grün.
- FFmpeg Docker Build-Gate ist vorhanden.
- Backend, Process Manager und Worker prüfen ffmpeg/ffprobe.
- Tests sollen ffmpeg-frei und gemockt bleiben.
- `docs-status.json` kann durch generierte Datumswerte CI-Diffs verursachen.
- Remote-URL-Lowercase funktioniert per Redirect, sollte aber sauber dokumentiert werden.

## Technische Bereiche

- Backend
- Frontend
- Worker
- Process Manager
- Docker Compose
- Preflight
- CI/CD
- Dokumentation
- Release-Prozess

## Stärken

- reale Docker-first Struktur
- Preflight als Startgate
- Build-Gates für kritische Runtime-Abhängigkeiten
- CI-Erfahrung
- klare Lessons Learned aus echten Fehlern

## Hauptrisiken

- generierte Dokumentationsstatus-Dateien
- zu starke Kopplung an externe Binaries in Tests
- wachsende Suite-Komplexität
- zu große KI-Arbeitspakete
- fehlende langfristige Release-/Docs-Navigation

## Nächster Meilenstein

NDF-Baseline committen, danach erstes technisches Work Package:

```text
docs-status.json Stabilität
```

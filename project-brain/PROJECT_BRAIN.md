# Project Brain – CastCore

## Projektstatus

CastCore ist ein aktives self-hosted Medien-/Processing-/Streaming-Suite-Projekt.

## Aktueller NDF-Status

NDF Baseline angelegt.

## Ziel

CastCore soll stabil, dokumentiert, Docker-first, testbar und releasefähig weiterentwickelt werden.

## Architekturstand

Bekannte Hauptbereiche:

- Backend
- Frontend
- Worker
- Process Manager
- Docker Compose
- Preflight
- CI/CD
- Dokumentation

## Wichtige Entscheidungen

- Docker-first.
- Preflight als zentrales Start-/Readiness-Gate.
- FFmpeg-Versionen werden kontrolliert.
- Tests sollen keine echte ffmpeg/ffprobe-Binary benötigen.
- Claude arbeitet nur in kleinen Work Packages.
- Kay prüft, committet und pusht.

## Bekannte Risiken

- `docs-status.json` kann CI-Diffs verursachen.
- Docker- und FFmpeg-Versionen müssen stabil gehalten werden.
- Suite-Komplexität kann Dokumentation überholen.
- Externe Runtime-Abhängigkeiten dürfen Tests nicht instabil machen.

## Aktuelle Priorität

```text
docs-status.json Stabilität
```

## Nächste Arbeitspakete

1. CC-WP-002 docs-status Stabilität
2. CC-WP-003 Health Score Review
3. CC-WP-004 Release Readiness Review

## Rückmeldung an Nova

Nach jedem Claude-Arbeitspaket erforderlich.

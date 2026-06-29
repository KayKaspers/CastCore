# Import-Anleitung – CastCore NDF Baseline

## Zielrepository

Dieses Paket gehört in das **CastCore-Repository**, nicht in das NDF-Repository.

## Schritte

1. ZIP entpacken.
2. Inhalt in das CastCore-Repository kopieren.
3. GitHub Desktop öffnen.
4. Änderungen prüfen.
5. Sicherstellen, dass keine Code-/CI-/Docker-Dateien geändert wurden.
6. Commit-Nachricht:

```text
docs(ndf): add CastCore NDF baseline
```

7. Commit to main.
8. Push origin.

## Erwartete geänderte Bereiche

```text
project-system/
project-brain/
docs/ndf/
docs/adr/
prompts/claude/
README_NDF_BASELINE.md
CASTCORE_NDF_BASELINE_IMPORT_ANLEITUNG.md
CHANGELOG_NDF_BASELINE.md
```

## Nicht erwartet

Keine Änderungen an:

```text
backend/
frontend/
worker/
process-manager/
.github/workflows/
Dockerfile
docker-compose.yml
package.json
```

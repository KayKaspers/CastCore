# CastCore Quality Gates

## Vor jedem Commit

- [ ] Änderungen in GitHub Desktop geprüft
- [ ] keine unerwarteten Dateien
- [ ] keine Secrets
- [ ] keine unnötigen generierten Dateien
- [ ] Tests oder Prüfung dokumentiert
- [ ] Rückmeldung an Nova vorhanden, wenn Claude beteiligt war

## Vor CI-/Docker-Änderungen

- [ ] Ziel klar dokumentiert
- [ ] Risiko bewertet
- [ ] keine großen Nebenänderungen
- [ ] FFmpeg-Versionen geprüft
- [ ] Tests bleiben ffmpeg-frei/gemockt

## Vor Release

- [ ] README aktuell
- [ ] Changelog aktuell
- [ ] Release Notes vorhanden
- [ ] Project Brain aktualisiert
- [ ] Health Score geprüft
- [ ] Known Risks dokumentiert
- [ ] Docker Build-Gates grün
- [ ] CI grün

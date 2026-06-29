# Claude Prompt – CC-WP-002 docs-status Stability

## Rolle

Du bist Claude und arbeitest vorsichtig im CastCore-Repository.

## Ziel

Untersuche und stabilisiere das Verhalten von `docs-status.json`, damit CI nicht durch unnötige Datums-/Zeitänderungen fehlschlägt.

## Aufgabe

1. Finde, wo `docs-status.json` erzeugt oder aktualisiert wird.
2. Prüfe, ob ein generiertes Datum oder Timestamp enthalten ist.
3. Schlage eine stabile Lösung vor.
4. Wenn eindeutig sicher: setze eine minimale Änderung um.
5. Aktualisiere Dokumentation oder Kommentar, falls nötig.

## Mögliche Lösungen

- Datum deterministisch machen.
- Datum nur bei echten Inhaltsänderungen aktualisieren.
- generiertes Datum aus CI-Vergleich herausnehmen.
- klar dokumentieren, wann Regeneration erwartet wird.

## Grenzen

- Keine großen Refactorings.
- Keine unnötigen CI-Umbauten.
- Keine Änderungen an FFmpeg-Tests.
- Keine Änderungen an Docker Build-Gates.
- Kein Commit.
- Kein Push.

## Akzeptanzkriterien

- Ursache ist dokumentiert.
- Lösung ist minimal.
- CI-Risiko wird reduziert.
- Tests bleiben ffmpeg-frei/gemockt.

## Rückmeldung an Nova

Bitte am Ende:

1. Ursache
2. Geänderte Dateien
3. Lösung
4. Tests/Prüfung
5. Risiken
6. Empfehlung

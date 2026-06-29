# Lessons Learned – CastCore

## L-001 – Preflight als Core-Feature

Preflight ist nicht nur ein Zusatz, sondern ein zentraler Stabilitätsmechanismus.

## L-002 – CI muss ohne lokale Medien-Binaries funktionieren

Tests dürfen nicht davon abhängen, ob auf dem CI-Runner oder lokalen Rechner ffmpeg installiert ist.

## L-003 – Docker Build-Gates sind wertvoll

Kritische Runtime-Abhängigkeiten sollen früh geprüft werden.

## L-004 – Generierte Dateien müssen deterministisch sein

Dateien wie `docs-status.json` dürfen nicht unnötig durch Zeit-/Datumswerte schwanken.

## L-005 – KI-Arbeit braucht Rückmeldung an Nova

Jedes Claude-Arbeitspaket muss am Ende eine strukturierte Rückmeldung an Nova liefern.

# ADR-0003: FFmpeg Docker Build Gate

## Status

Accepted

## Kontext

CastCore hängt funktional von FFmpeg/ffprobe ab. Falsche Versionen können zur Laufzeit Probleme verursachen.

## Entscheidung

FFmpeg/ffprobe-Versionen werden über Docker Build-Gates geprüft.

## Konsequenzen

- Fehler werden früher erkannt.
- Images müssen klare FFmpeg-Versionen liefern.
- Build-Gates müssen verständliche Fehlermeldungen liefern.

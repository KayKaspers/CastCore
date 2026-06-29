# ADR-0004: FFmpeg-free Tests

## Status

Accepted

## Kontext

Tests können instabil werden, wenn sie eine lokal installierte ffmpeg/ffprobe-Binary erwarten.

## Entscheidung

Tests sollen FFmpeg/ffprobe mocken und keine echte lokale Binary voraussetzen.

## Konsequenzen

- CI wird stabiler.
- Entwickler brauchen lokal kein FFmpeg nur für Tests.
- Tests prüfen Logik statt externe Binary-Verfügbarkeit.

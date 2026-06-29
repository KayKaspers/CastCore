# Architektur- und Projektentscheidungen

## Entscheidungen

### Entscheidung 1 — Stack „Option A“

Datum: 2026-06-24
Entscheidung: Python 3.12 + FastAPI, SQLAlchemy 2 async + Alembic, PostgreSQL 16, Redis 7,
arq-Worker; Frontend React+TS+Vite+Tailwind+i18next+zustand; Caddy; optional MediaMTX.
Grund: ausgereiftes, async-fähiges, gut dokumentiertes Ökosystem; anfängerfreundlich deploybar.
Auswirkung: Docker-first-Stack als Standard; CI darauf ausgelegt.

### Entscheidung 2 — Dedizierter Process Manager (getrennt vom Worker)

Datum: 2026-06-24
Entscheidung: Langlaufende FFmpeg-Stream-Prozesse laufen in einem eigenen asyncio-Supervisor,
nicht im Task-Worker.
Grund: Streams sind langlebige, überwachte Prozesse — andere Lebensdauer/Fehlermodelle als kurze Jobs.
Auswirkung: Status fließt über Redis-PubSub zurück; Status-Consumer in der FastAPI-Lifespan reconciled DB/UI.

### Entscheidung 3 — Bilinguale, übersetzbare Fehler-Codes

Datum: 2026-06-24
Entscheidung: Backend liefert Fehler-*Codes* (z. B. `preflight.required`), Frontend übersetzt DE/EN.
Grund: harte Anforderung DE/EN; saubere Trennung von Logik und Darstellung.
Auswirkung: i18n-Schlüssel `error.<code>`; jede neue Fehlerquelle braucht DE+EN-Strings.

### Entscheidung 4 — Documentation-first (bindende Doku-Regel)

Datum: 2026-06-24
Entscheidung: Keine Feature-Änderung ohne paralleles DE+EN-Doku-Update + `check_docs.py`.
Grund: Doku als Produktqualität, nicht als Nachgedanke.
Auswirkung: CI-Job „docs“ bricht bei veralteten generierten Dateien ab.

### Entscheidung 5 — Preflight 2.0: persistierte Reports statt In-Memory-Cache

Datum: 2026-06-29
Entscheidung: Startklar-Prüfungen werden als strukturierte `PreflightReport`-Zeilen persistiert
(Migration 0016) und treiben optional ein Start-Gate (required / block-on-red, Admin-Override, auditiert).
Grund: Reports überstehen Neustarts, speisen Health-Score/Diagnose ohne erneutes Probing; Gate erhöht Betriebssicherheit.
Auswirkung: In-Memory `cache_preflight` entfernt; diagnostics/monitoring lesen aus der DB.

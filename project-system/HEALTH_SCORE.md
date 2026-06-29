# Health Score – CastCore

## Initiale Bewertung

| Dimension | Score | Notes |
|---|---:|---|
| Architecture | 78 | modulare Suite-Struktur vorhanden |
| Documentation | 74 | vorhanden, aber Stabilität/Navigation prüfen |
| Testing | 84 | ffmpeg-freie Tests sind starke Entscheidung |
| CI/CD | 85 | grüner Stand und Build-Gates bekannt |
| Security | 60 | vertiefter Review offen |
| Deployment | 84 | Docker-first stark |
| Project Brain | 75 | Baseline vorhanden, muss gepflegt werden |
| Prompt Workflow | 82 | Nova/Claude-Prozess etabliert |
| Release Readiness | 66 | Prozess weiter schärfen |

## Total (initial)

76 / 100

---

## Update nach CC-WP-002 (docs-status Stability)

Review-Datum: 2026-06-29 · Auslöser: Abschluss `CC-WP-002`.

| Dimension | Alt | Neu | Δ | Begründung |
|---|---:|---:|---:|---|
| Architecture | 78 | 78 | 0 | CC-WP-002 war reines Doku-Tooling, keine Architekturänderung. |
| Documentation | 74 | 78 | +4 | `docs-status.json`-Generierung jetzt deterministisch und als reine Funktion des Doku-Inhalts; Generierungspipeline vertrauenswürdiger. |
| Testing | 84 | 84 | 0 | Keine Teständerungen; Tests bleiben ffmpeg-frei/gemockt. Determinismus wurde via Skriptlauf (Hash-Vergleich) geprüft, nicht via Unit-Test. |
| CI/CD | 85 | 90 | +5 | Tägliche Falsch-Fehlschläge im Docs-Gate (datumsbedingter `git diff`) beseitigt; CI-Signal stabiler und aussagekräftiger. |
| Security | 60 | 60 | 0 | Vertiefter Security-Review weiterhin offen (CC-WP-006). |
| Deployment | 84 | 84 | 0 | Unverändert; Docker-first nicht berührt. |
| Project Brain | 75 | 77 | +2 | R-001 ist durch CC-WP-002 mitigiert, L-004 in der Praxis bestätigt; das Brain zeigt nachweislich Vorhersagewert. Pflege weiterhin nötig. |
| Prompt Workflow | 82 | 85 | +3 | Nova→Claude→Cursor-WP-Prozess sauber durchlaufen (kleines Paket, klare Grenzen, strukturierte Rückmeldung). |
| Release Readiness | 66 | 70 | +4 | Eine CI-Flakiness-Quelle als Release-Blocker entfernt; vollständiger Release-Readiness-Review (CC-WP-004) steht aber noch aus. |

## Total

**78 / 100** (vorher 76)

Wichtigste Veränderungen: CI/CD (+5), Documentation (+4), Release Readiness (+4).

## Interpretation

CastCore bleibt ein solides NDF-Level-3-Projekt; durch die stabilere Doku-/CI-Pipeline rückt Level 4 etwas näher. Der größte verbleibende Hebel ist der noch offene Security-Review.

## Offene Risiken

- **Restdatumsabhängigkeit (neu):** `summary.stale` und `summary.warnings` in `docs-status.json` reagieren weiterhin auf Datumsschwellen (`STALE_DAYS=180`). Aktuell `stale: 0`, daher kein akutes Problem, aber langfristig erneut eine mögliche CI-Diff-Quelle. Bezug: R-001 (Teilrest).
- **Security-Review offen:** Dimension Security bleibt bei 60 (CC-WP-006 ausstehend).
- **Release Readiness unvollständig geprüft:** CC-WP-004 noch nicht durchgeführt.
- **README-NDF-Abschnitt offen:** CC-WP-005 noch im Draft.
- **Hinweis:** Der Health Score ist eine Review-Hilfe, keine absolute Wahrheit.

## Empfohlene nächste Work Packages

1. **CC-WP-006 – Security baseline review** (P2): größter Score-Hebel (Security 60).
2. **CC-WP-004 – Release Readiness Review** (P2): Release-Readiness von 70 auf belastbares Niveau heben.
3. **CC-WP-005 – README NDF section** (P3): NDF-Sichtbarkeit nach außen schließen.
4. **Optionales Folge-WP:** Restdatumsabhängigkeit von `summary.stale`/`summary.warnings` adressieren (Stale nur als CI-Log-Warnung, nicht im committeten Artefakt).

---

## Update nach CC-WP-007 (Fail-closed Secret Validation)

Review-Datum: 2026-06-29 · Auslöser: Abschluss `CC-WP-007` (Mitigation von `SEC-01`).
Voraus ging `CC-WP-006` (Security Baseline Review), das die Findings strukturiert und
`SEC-01` als Finding hoher Schwere identifiziert hat (ohne Score-Änderung).

| Dimension | Alt | Neu | Δ | Begründung |
|---|---:|---:|---:|---|
| Security | 60 | 66 | +6 | `SEC-01` technisch mitigiert: Production startet fail-closed nicht mehr mit unsicheren Defaults (`SECRET_KEY`/`ENCRYPTION_KEY`/`POSTGRES_PASSWORD`), per Unit-Test abgesichert (5 passed). Echte Posture-Verbesserung, nicht nur Doku. |

Alle übrigen Dimensionen unverändert gegenüber dem Stand nach CC-WP-002
(Architecture 78 · Documentation 78 · Testing 84 · CI/CD 90 · Deployment 84 ·
Project Brain 77 · Prompt Workflow 85 · Release Readiness 70).

## Total (nach CC-WP-007)

**79 / 100** (vorher 78)

Wichtigste Veränderung: Security 60 → 66 (+6).

**Die Erhöhung bleibt bewusst moderat:** SEC-01 ist nur *ein* Finding der Baseline. Offen
bleiben u. a. CSP-Header (SEC-02), non-root für backend/process-manager (SEC-03) und
Security-Automation/SCA in CI (SEC-07). Erst deren Umsetzung rechtfertigt einen weiteren
Security-Sprung.

## Offene Security-Risiken (Stand nach CC-WP-007)

- **SEC-02 (Mittel):** Kein CSP-Header gesetzt → `CC-WP-008`.
- **SEC-03 (Mittel):** backend & process-manager laufen weiterhin als root → `CC-WP-009`.
- **SEC-04 (Mittel):** gepatchtes FFmpeg ≥ 8.1.2 noch nicht verifiziertes Default-Binary (mitigiert via Versionserkennung + Safe-Media-Mode).
- **SEC-05 (Niedrig):** Rate-Limiting nur auf Auth-Endpoints; fällt bei Redis-Ausfall offen.
- **SEC-06 (Niedrig):** OAuth-Metadata-Push nicht gegen Live-APIs verifiziert.
- **SEC-07 (Niedrig):** keine Security-Automation (SCA/Secret-Scan) in CI → `CC-WP-010`.
- **SEC-01-Reststand:** Guard greift bei Defaults/Platzhaltern/kurzen Keys, prüft aber keine echte Passwort-Entropie; `REDIS_PASSWORD` bleibt intern optional. Siehe `R-006`.
- **Hinweis:** Der Health Score ist eine Review-Hilfe, keine absolute Wahrheit.

## Empfohlene nächste Work Packages (nach CC-WP-007)

1. **CC-WP-008 – CSP-Header am Reverse-Proxy** (P2): nächster Security-Hebel.
2. **CC-WP-009 – Non-root für backend/process-manager** (P2).
3. **CC-WP-004 – Release Readiness Review** (P2): Readiness von 70 auf belastbares Niveau.
4. **CC-WP-010 – Security-Automation in CI** (P3, nur nach Nova-Entscheid wg. CI-Grenzen).
5. **CC-WP-005 – README NDF section** (P3).

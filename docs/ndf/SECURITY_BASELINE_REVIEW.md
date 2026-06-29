# Security Baseline Review – CastCore

> NDF Work Package **CC-WP-006** · Review-Datum: 2026-06-29 · Reviewer: Claude (NDF)
> Typ: **erste Security-Baseline**, kein vollständiges Audit · **keine Codeänderungen**

Dieses Dokument ist eine strukturierte Erst-Bewertung der Security-Lage von CastCore auf
Basis von Dokumentation, Konfiguration und einer leichten Quell-Stichprobe. Es ersetzt
**kein** vollständiges Security-Audit (kein Pentest, keine Dependency-/SCA-Analyse, keine
Laufzeit-Tests). Es wurden **keine Secrets offengelegt oder kopiert.**

## 1. Methode

Geprüft wurde auf Dokumentations- und Konfigurationsebene plus eine read-only Stichprobe im
Quellcode (nur zur Verifikation dokumentierter Aussagen, keine Änderungen):

- [`docs/SECURITY.md`](../SECURITY.md), [`.env.example`](../../.env.example),
  [`.gitignore`](../../.gitignore), [`docker-compose.yml`](../../docker-compose.yml),
  [`backend/app/core/config.py`](../../backend/app/core/config.py).
- `git ls-files` / `git grep` auf Secret- und Unsafe-Patterns (Ergebnisse nur als Fundort,
  nie als Wert).

**Verifiziert (grounding):**

| Behauptung in SECURITY.md | Befund der Stichprobe |
|---|---|
| Kein Shell-Exec (`shell=False`) | `shell=True` in backend/process_manager/worker: **keine Treffer** |
| argon2id / Fernet / JWT im Einsatz | argon2 (2 Dateien), Fernet (6), jwt (6) vorhanden |
| Keine hardcoded Secrets im Code | Keine inline `password=/secret=/api_key=`-Stringzuweisungen; keine `BEGIN PRIVATE KEY` |
| `.env` nicht im Repo | Nur `.env.example` (mit `changeme_`-Platzhaltern) getrackt; kein echtes `.env` |
| Secret-Dateien gitignored | `.env`, `.env.*`, `*.key`, `*.pem`, `secrets/` in `.gitignore` |

## 2. Bewertung nach Bereichen

| Bereich | Stand | Bewertung |
|---|---|---|
| **Authentifizierung** | 🟢 gut | argon2id-Hashing, JWT-Access + rotierende/revozierbare Refresh-Tokens (gehasht gespeichert), 2FA (TOTP, Secret verschlüsselt), API-Tokens (`cc_`-Präfix, gehasht). |
| **Autorisierung (RBAC)** | 🟢 gut | Rollen Admin/Operator/Viewer, serverseitig pro Endpoint erzwungen (dokumentiert). |
| **Secret-Handling** | 🟢 gut | Fernet-Verschlüsselung at rest, write-only über API, maskierte Rückgabe, nicht geloggt; `ENCRYPTION_KEY` aus Env, getrennt zu sichern. |
| **Transport / Web** | 🟡 teilweise | HTTPS via Caddy; Bearer-API (CSRF N/A); HSTS/X-Content-Type-Options/Referrer-Policy gesetzt. **CSP fehlt** (TODO). Rate-Limiting nur auf Auth-Endpoints; breitere Limits offen. |
| **FFmpeg / System-Safety** | 🟡 teilweise | `shell=False` durchgängig, Argument-Listen, Pfad-Confinement, sichere Uploads, minimale Prozess-Env, Mount-Creds in `0600`-Dateien. **Aber:** gepatchtes FFmpeg ≥ 8.1.2 ist noch nicht das verifizierte Default-Binary (Mitigation via Versions-Erkennung + Safe-Media-Mode). |
| **Audit / Betrieb** | 🟢 gut | Audit-Log für sicherheitsrelevante Aktionen (Actor/Target/IP/Zeit), restriktive Dateirechte, dedizierter `castcore`-User (native). |
| **Container-Hardening** | 🟡 teilweise | `no-new-privileges` überall; Worker `cap_drop: ALL` + non-root. **Backend & process-manager laufen weiterhin als root** (optionale In-Container-Mounts brauchen `SYS_ADMIN`) — bekannter Gap. |
| **Konfig-Defaults** | 🔴 Finding | Unsichere Fallback-Defaults ohne Fail-Closed-Validierung (siehe SEC-01). |
| **Secrets im Repo** | 🟢 gut | Keine echten Secrets getrackt; nur Platzhalter-Template. |

## 3. Findings (priorisiert)

| ID | Schwere | Bereich | Beschreibung | Status |
|---|---|---|---|---|
| **SEC-01** | **Hoch** | Konfig-Defaults | `config.py` hat unsichere Fallbacks: `secret_key="changeme"`, `encryption_key=""`, `postgres_password="castcore"`. Es gibt **keine Startup-Validierung**, die in `production` erzwingt, dass diese gesetzt/stark sind (fail-closed). Folge: Startet die App ohne korrekt gesetzte Env, entstehen fälschbare JWTs (`changeme`). `.env.example` und Compose adressieren das nur per Konvention, nicht erzwingend. | offen |
| **SEC-02** | Mittel | Transport/Web | **Kein CSP-Header** gesetzt (dokumentierter TODO). | offen |
| **SEC-03** | Mittel | Container | Backend & process-manager laufen als **root** (nur `no-new-privileges`). | offen (bekannt) |
| **SEC-04** | Mittel | Media-Safety | Gepatchtes **FFmpeg ≥ 8.1.2** ist noch nicht das verifizierte Default-Binary; Schutz aktuell über Versions-Erkennung + Safe-Media-Mode (CVE-2026-8461). | mitigiert, offen |
| **SEC-05** | Niedrig | Rate-Limiting | Throttling nur auf Auth-Endpoints; breitere per-Endpoint-Limits fehlen. Fällt zudem **offen** bei nicht erreichbarem Redis. | offen |
| **SEC-06** | Niedrig | OAuth | Platform-Metadata-Push gegen Live-APIs noch **nicht verifiziert**; nur mit gemockten APIs getestet. | offen |
| **SEC-07** | Niedrig | Tests | Keine Frontend-/Migration-Tests; kein automatisierter Security-Test (SCA/Secret-Scan in CI). | offen |

> Hinweis: SEC-04 deckt sich mit dem dokumentierten FFmpeg-Gap; SEC-07 ergänzt die
> bestehende Risikolage um eine Automatisierungslücke.

## 4. Empfohlene nächste Security Work Packages

Priorisiert nach Wirkung/Aufwand:

1. **CC-WP-007 – Fail-closed Secret-Validierung (SEC-01):** In `config.py` beim Start in
   `production` abbrechen, wenn `SECRET_KEY`/`ENCRYPTION_KEY`/`POSTGRES_PASSWORD` leer oder
   Default sind (`changeme`/`castcore`). *Größter Hebel, kleiner, klar abgegrenzter Eingriff —
   benötigt eigenes Code-WP mit Nova-Freigabe.*
2. **CC-WP-008 – CSP-Header am Reverse-Proxy (SEC-02):** restriktive Content-Security-Policy
   in der Caddy-/Nginx-Konfiguration.
3. **CC-WP-009 – Non-root für backend/process-manager (SEC-03):** non-root als Default,
   In-Container-Mounts als opt-in dokumentieren.
4. **CC-WP-010 – Security-Automation in CI:** Secret-Scan + Dependency-/SCA-Check
   (z. B. `pip-audit`/`npm audit`) als nicht-blockierender Report. *(CI-Änderung — nur nach
   Nova-Entscheid, da außerhalb der aktuellen CI-Grenzen.)*
5. **CC-WP-011 – Vollständiges Security-Audit:** Pentest-orientierte Prüfung der Live-Pfade
   (OAuth, Upload, Mount, Stream-Start), sobald 1–4 erledigt sind.

## 5. Grenzen dieser Baseline

- Kein Pentest, keine Laufzeit-/Fuzzing-Tests, keine Dependency-CVE-Analyse.
- Quellprüfung war stichprobenartig (Verifikation dokumentierter Aussagen), kein
  Zeilen-für-Zeile-Audit der Auth-/Crypto-Pfade.
- Der Health-Score-Wert „Security" bleibt eine Review-Hilfe, keine absolute Wahrheit.

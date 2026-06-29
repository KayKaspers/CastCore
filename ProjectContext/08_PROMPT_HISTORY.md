# Prompt-Verlauf

Hier werden wichtige Claude-Prompts dokumentiert.

## Format

### Datum – Schritt

Prompt:
Ergebnis:
Rückmeldung an Nova:

---

### 2026-06-29 – Repo-Umzug + Preflight 2.0 sichern, verifizieren, committen

Prompt: „Continue from where you left off“ → neues Verzeichnis `D:\Projects\CastCore`;
danach: Preflight 2.0 verifizieren und committen (check_docs, pytest, ruff, mypy,
Frontend lint/build, compose config), dann ProjectContext befüllen, dann Übergabe an Nova.

Ergebnis:
- Uncommittete Preflight-2.0-Arbeit aus altem Nextcloud-Ordner per Patch ins neue Repo übernommen.
- Frontend an neue API angeglichen; Doku DE+EN auf 2.0 aktualisiert.
- `.env` neu generiert; Postgres-Passwort non-destruktiv angeglichen.
- Alle Checks grün; Commit `d7e306a` (23 Dateien). ProjectContext aus realem Stand befüllt.

Rückmeldung an Nova: siehe Übergabe (Was/Dateien/Tests/Docs/README/Preflight/ProjectContext/
Risiken/nächster Schritt). Offen: Push nach GitHub auf Freigabe.

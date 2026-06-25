#!/usr/bin/env bash
# Scaffolds the bilingual CastCore docs tree (docs/de + docs/en) with non-empty,
# templated stub pages. Idempotent for missing files; never overwrites existing pages
# (so hand-written cornerstone pages are preserved). Run from the repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS="$ROOT/docs"
TODAY="2026-06-24"

aud_de() { case "$1" in getting-started*) echo "Einsteiger";; user-guide*) echo "Anwender / Operatoren";; admin-guide*) echo "Administratoren";; developer-guide*) echo "Entwickler";; api*) echo "Entwickler / Integratoren";; reference*) echo "Alle Rollen";; troubleshooting*) echo "Operatoren / Administratoren";; *) echo "Alle Rollen";; esac; }
aud_en() { case "$1" in getting-started*) echo "Beginners";; user-guide*) echo "Users / Operators";; admin-guide*) echo "Administrators";; developer-guide*) echo "Developers";; api*) echo "Developers / Integrators";; reference*) echo "All roles";; troubleshooting*) echo "Operators / Administrators";; *) echo "All roles";; esac; }

write_page() {
  # $1 lang  $2 relpath  $3 title  $4 desc  $5 audience  $6 status
  local lang="$1" rel="$2" title="$3" desc="$4" aud="$5" status="$6"
  local file="$DOCS/$lang/$rel"
  [ -f "$file" ] && return 0
  mkdir -p "$(dirname "$file")"
  if [ "$lang" = "de" ]; then
    cat > "$file" <<EOF
---
title: "$title"
description: "$desc"
lang: de
audience: "$aud"
status: $status
lastReviewed: $TODAY
---

# $title

> $desc

**Zielgruppe:** $aud

## Überblick

$desc

## Inhalt

> ⚠️ **Entwurf** – Diese Seite ist angelegt und beschreibt das Thema, wird aber noch um Details, Beispiele und Screenshots ergänzt.

- TODO: Schritt-für-Schritt-Anleitung bzw. ausführliche Erklärung ergänzen.

## Hinweise

- Sicherheit: siehe [Security Best Practices](/docs/de/admin-guide/security.md).

## Verwandte Seiten

- [Dokumentations-Startseite](/docs/de/index.md)
- [Glossar](/docs/de/reference/glossary.md)

---
_Stand: $TODAY · Status: Entwurf · Sprache: Deutsch (Hauptsprache)_
EOF
  else
    cat > "$file" <<EOF
---
title: "$title"
description: "$desc"
lang: en
audience: "$aud"
status: $status
lastReviewed: $TODAY
---

# $title

> $desc

**Audience:** $aud

## Overview

$desc

## Contents

> ⚠️ **Draft** – This page exists and describes the topic, but details, examples and screenshots are still being added.

- TODO: add the step-by-step guide or in-depth explanation.

## Notes

- Security: see [Security best practices](/docs/en/admin-guide/security.md).

## Related pages

- [Documentation home](/docs/en/index.md)
- [Glossary](/docs/en/reference/glossary.md)

---
_Last reviewed: $TODAY · Status: draft · Language: English_
EOF
  fi
}

# relpath|de_title|en_title|de_desc|en_desc
DATA=$(cat <<'LIST'
index.md|CastCore Dokumentation|CastCore Documentation|Einstieg in die CastCore-Dokumentation – Self-Hosted Streaming Operations Suite.|Entry point to the CastCore documentation – self-hosted streaming operations suite.
getting-started/overview.md|Was ist CastCore?|What is CastCore?|Überblick über Zweck, Zielgruppe und Funktionsumfang von CastCore.|Overview of CastCore's purpose, audience and capabilities.
getting-started/installation-docker.md|Installation mit Docker Compose|Install with Docker Compose|CastCore mit Docker Compose auf einem frischen Linux-System installieren.|Install CastCore with Docker Compose on a fresh Linux system.
getting-started/installation-native.md|Native Linux-Installation|Native Linux installation|CastCore ohne Docker über die Installationsskripte einrichten.|Set up CastCore without Docker using the install scripts.
getting-started/first-setup.md|Setup-Assistent (Ersteinrichtung)|Setup wizard (first run)|Den Setup-Assistenten durchlaufen: Sprache, Admin, Systemcheck.|Walk through the setup wizard: language, admin, system check.
getting-started/quickstart.md|Schnellstart: Erster Stream|Quickstart: your first stream|In wenigen Minuten vom Login zum ersten laufenden Teststream.|From login to your first running test stream in minutes.
user-guide/dashboard.md|Dashboard|Dashboard|Das Dashboard liest Systemzustand und aktive Streams auf einen Blick.|The dashboard shows system health and active streams at a glance.
user-guide/streams.md|Stream-Jobs|Stream jobs|Stream-Jobs anlegen, starten, stoppen und überwachen.|Create, start, stop and monitor stream jobs.
user-guide/stream-editor.md|Stream-Editor|Stream editor|Inputs, Outputs, Profil und Recording eines Streams konfigurieren.|Configure a stream's inputs, outputs, profile and recording.
user-guide/sources-storage.md|Quellen / Storage|Sources / storage|Lokale und Netzwerk-Quellen (SMB) anlegen, testen, mounten, durchsuchen.|Create, test, mount and browse local and network (SMB) sources.
user-guide/media-library.md|Medienbibliothek|Media library|Quellen scannen, Medien per ffprobe indexieren und als Input wählen.|Scan sources, index media via ffprobe and pick them as inputs.
user-guide/playlists.md|Playlists|Playlists|Geordnete/zufällige Medienlisten als Grundlage für Channels.|Ordered/shuffled media lists as the basis for channels.
user-guide/channels.md|Channels (lineares Playout)|Channels (linear playout)|24/7-Channels aus Playlists mit HLS-Output, EPG und M3U.|24/7 channels from playlists with HLS output, EPG and M3U.
user-guide/platforms.md|Plattformen|Platforms|Ausgabeziele und Plattformen (Twitch, YouTube, RTMP) verwalten.|Manage output destinations and platforms (Twitch, YouTube, RTMP).
user-guide/metadata-thumbnails.md|Metadaten & Thumbnails|Metadata & thumbnails|Plattform-Metadaten und Beschreibungsvorlagen mit Platzhaltern pflegen.|Manage platform metadata and description templates with placeholders.
user-guide/recordings-replay.md|Recordings & Replay|Recordings & replay|Streams aufnehmen, Aufnahmen verwalten und herunterladen.|Record streams, manage and download recordings.
user-guide/monitoring.md|Monitoring|Monitoring|System- und Stream-Metriken live: CPU, RAM, FPS, Bitrate.|Live system and stream metrics: CPU, RAM, FPS, bitrate.
user-guide/preflight-checks.md|Preflight-Checks|Preflight checks|Vor dem Start prüfen, ob ein Job startklar ist (Ampel).|Check before start whether a job is ready (traffic light).
user-guide/settings.md|Einstellungen|Settings|Allgemeine und benutzerbezogene Einstellungen.|General and per-user settings.
user-guide/users-roles.md|Benutzer & Rollen|Users & roles|Benutzer verwalten und Rollen (Admin/Operator/Viewer) vergeben.|Manage users and assign roles (Admin/Operator/Viewer).
user-guide/backup-restore.md|Backup & Restore|Backup & restore|Datenbank und Konfiguration sichern und wiederherstellen.|Back up and restore the database and configuration.
user-guide/updates.md|Updates|Updates|CastCore aktualisieren (Docker und nativ).|Update CastCore (Docker and native).
admin-guide/system-requirements.md|Systemanforderungen|System requirements|Hardware-, OS- und Netzwerk-Voraussetzungen für CastCore.|Hardware, OS and network requirements for CastCore.
admin-guide/deployment.md|Deployment|Deployment|Überblick über die Deployment-Wege und Betriebsmodelle.|Overview of deployment paths and operating models.
admin-guide/docker-compose.md|Docker-Compose-Betrieb|Operating with Docker Compose|Services, Volumes, Healthchecks und Profile der Compose-Datei.|Services, volumes, healthchecks and profiles of the compose file.
admin-guide/reverse-proxy.md|Reverse Proxy|Reverse proxy|Caddy (Standard) oder Nginx vor CastCore betreiben.|Run Caddy (default) or Nginx in front of CastCore.
admin-guide/https.md|HTTPS / TLS|HTTPS / TLS|Automatische und manuelle Zertifikate für CastCore.|Automatic and manual certificates for CastCore.
admin-guide/storage-mounts.md|Storage-Mounts|Storage mounts|Host- vs. Container-Mounts und Datenverzeichnisse.|Host vs. container mounts and data directories.
admin-guide/smb-cifs.md|SMB / CIFS|SMB / CIFS|SMB-Freigaben sicher einbinden (Credentials, Mounts).|Mount SMB shares securely (credentials, mounts).
admin-guide/nfs.md|NFS|NFS|NFS-Exporte als Quelle einbinden.|Use NFS exports as a source.
admin-guide/cloud-sources.md|Cloud-Quellen|Cloud sources|S3/WebDAV/rclone-Remotes als Quelle vorbereiten.|Prepare S3/WebDAV/rclone remotes as sources.
admin-guide/security.md|Security Best Practices|Security best practices|Härtung, Rollen, Secrets, sichere Uploads, Audit.|Hardening, roles, secrets, safe uploads, audit.
admin-guide/secrets.md|Secrets-Verwaltung|Secrets management|Verschlüsselung (Fernet), ENCRYPTION_KEY, Schlüsselrotation.|Encryption (Fernet), ENCRYPTION_KEY, key rotation.
admin-guide/logs.md|Logs|Logs|Wo CastCore-Logs liegen und wie man sie liest.|Where CastCore logs live and how to read them.
admin-guide/troubleshooting.md|Troubleshooting (Admin)|Troubleshooting (admin)|Einstieg in die Fehlersuche für Administratoren.|Entry point to troubleshooting for administrators.
developer-guide/architecture.md|Architektur|Architecture|Zielarchitektur, Komponenten und Datenfluss von CastCore.|Target architecture, components and data flow of CastCore.
developer-guide/project-structure.md|Projektstruktur|Project structure|Verzeichnislayout des Monorepos.|Directory layout of the monorepo.
developer-guide/backend.md|Backend|Backend|FastAPI-Backend: Aufbau, Services, Dependencies.|FastAPI backend: structure, services, dependencies.
developer-guide/frontend.md|Frontend|Frontend|React/Vite-Frontend: Aufbau, State, i18n.|React/Vite frontend: structure, state, i18n.
developer-guide/database.md|Datenbank|Database|PostgreSQL-Schema und SQLAlchemy-Modelle.|PostgreSQL schema and SQLAlchemy models.
developer-guide/migrations.md|Migrationen|Migrations|Alembic-Migrationen erstellen und anwenden.|Create and apply Alembic migrations.
developer-guide/api.md|API (Entwickler)|API (developer)|REST/WS-API-Aufbau, OpenAPI, typed client.|REST/WS API structure, OpenAPI, typed client.
developer-guide/websocket-sse.md|WebSockets / SSE|WebSockets / SSE|Live-Logs und Status über WebSockets.|Live logs and status over WebSockets.
developer-guide/ffmpeg-command-builder.md|FFmpeg Command Builder|FFmpeg command builder|Sichere argv-Konstruktion ohne Shell.|Safe argv construction without a shell.
developer-guide/process-manager.md|Process Manager|Process manager|Supervidierung langlaufender FFmpeg-Prozesse.|Supervision of long-running FFmpeg processes.
developer-guide/platform-integrations.md|Plattform-Integrationen|Platform integrations|Plattform-/Metadaten-Schicht und Erweiterung.|Platform/metadata layer and how to extend it.
developer-guide/storage-integrations.md|Storage-Integrationen|Storage integrations|Quellen-/Mount-Schicht und Erweiterung.|Source/mount layer and how to extend it.
developer-guide/media-library.md|Medienbibliothek (Entwickler)|Media library (developer)|Scan-/ffprobe-Pipeline der Medienbibliothek.|Scan/ffprobe pipeline of the media library.
developer-guide/testing.md|Tests, Linting, Typprüfung|Testing, linting, type checks|pytest, ruff, mypy, tsc – lokal und in CI.|pytest, ruff, mypy, tsc – locally and in CI.
developer-guide/contributing.md|Mitwirken (Entwickler)|Contributing (developer)|Workflow, Branches, Commits, Definition of Done.|Workflow, branches, commits, definition of done.
developer-guide/documentation-rules.md|Dokumentationsregeln|Documentation rules|Verbindliche Regel: keine Feature-Änderung ohne Docs-Update.|Binding rule: no feature change without a docs update.
api/overview.md|API-Überblick|API overview|Basis-URL, Auth, Fehlerformat, OpenAPI/Swagger.|Base URL, auth, error format, OpenAPI/Swagger.
api/auth.md|API: Auth|API: auth|Login, JWT-Refresh, Logout, API-Tokens.|Login, JWT refresh, logout, API tokens.
api/streams.md|API: Streams|API: streams|Stream-Jobs, Profile, Start/Stop, Preflight.|Stream jobs, profiles, start/stop, preflight.
api/sources.md|API: Quellen|API: sources|Storage-Quellen, Test, Mount, Browse.|Storage sources, test, mount, browse.
api/platforms.md|API: Plattformen & Metadaten|API: platforms & metadata|Destinations und Plattform-Metadaten/Templates.|Destinations and platform metadata/templates.
api/media-library.md|API: Medienbibliothek|API: media library|Scan, Auflistung, ffprobe-Daten.|Scan, listing, ffprobe data.
api/monitoring.md|API: Monitoring|API: monitoring|System- und Output-Metriken.|System and output metrics.
api/backup-restore.md|API: Backup/Restore|API: backup/restore|Backups erstellen, herunterladen, wiederherstellen.|Create, download and restore backups.
reference/configuration.md|Konfiguration|Configuration|Alle Konfigurationsoptionen im Überblick.|All configuration options at a glance.
reference/environment-variables.md|Umgebungsvariablen|Environment variables|Referenz aller `.env`-Variablen.|Reference of all `.env` variables.
reference/permissions.md|Berechtigungen|Permissions|Welche Aktion welche Rolle erfordert.|Which action requires which role.
reference/roles.md|Rollen|Roles|Admin, Operator, Viewer im Detail.|Admin, Operator, Viewer in detail.
reference/ffmpeg-profiles.md|FFmpeg-Profile|FFmpeg profiles|Felder eines FFmpeg-Profils und ihre Wirkung.|Fields of an FFmpeg profile and their effect.
reference/placeholders.md|Platzhalter (Templates)|Placeholders (templates)|Alle Platzhalter für Beschreibungsvorlagen.|All placeholders for description templates.
reference/glossary.md|Glossar|Glossary|Zweisprachiges Glossar der Streaming-Begriffe.|Bilingual glossary of streaming terms.
troubleshooting/index.md|Troubleshooting|Troubleshooting|Einstieg in die Fehlersuche nach Symptom.|Entry point to troubleshooting by symptom.
troubleshooting/ffmpeg-errors.md|FFmpeg-Fehler|FFmpeg errors|Häufige FFmpeg-Fehler erkennen und beheben.|Identify and fix common FFmpeg errors.
troubleshooting/stream-not-starting.md|Stream startet nicht|Stream not starting|Diagnose, wenn ein Stream nicht startet.|Diagnose when a stream won't start.
troubleshooting/smb-problems.md|SMB-Probleme|SMB problems|SMB-Mount- und Zugriffsfehler lösen.|Resolve SMB mount and access errors.
troubleshooting/platform-errors.md|Plattform-Fehler|Platform errors|RTMP rejected, falscher Stream-Key, API-Fehler.|RTMP rejected, wrong stream key, API errors.
troubleshooting/performance.md|Performance|Performance|Encoding-Speed < 1.0x, hohe CPU, Engpässe.|Encoding speed < 1.0x, high CPU, bottlenecks.
troubleshooting/docker.md|Docker-Probleme|Docker problems|Container starten nicht, DB/Redis nicht erreichbar.|Containers won't start, DB/Redis unreachable.
troubleshooting/native-installation.md|Native Installation|Native installation|Probleme bei der nativen Installation.|Problems with the native installation.
LIST
)

count=0
while IFS='|' read -r rel de_t en_t de_d en_d; do
  [ -z "$rel" ] && continue
  status="draft"; case "$rel" in index.md) status="stable";; esac
  write_page de "$rel" "$de_t" "$de_d" "$(aud_de "$rel")" "$status"
  write_page en "$rel" "$en_t" "$en_d" "$(aud_en "$rel")" "$status"
  count=$((count+2))
done <<< "$DATA"

# asset + template dirs
mkdir -p "$DOCS/assets/images" "$DOCS/assets/screenshots/de" "$DOCS/assets/screenshots/en" "$DOCS/assets/diagrams" "$DOCS/assets/logos"
echo "scaffold complete: $count files ensured"

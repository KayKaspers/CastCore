#!/usr/bin/env bash
# CastCore — native installer for Debian 12 / Ubuntu Server LTS.
# Assumes a clean Linux system. Run as root: sudo ./scripts/install.sh
set -euo pipefail

APP_USER="castcore"
APP_DIR="/opt/castcore"
DATA_DIR="/var/lib/castcore"
LOG_DIR="/var/log/castcore"
ETC_DIR="/etc/castcore"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log()  { printf '\033[1;32m[castcore]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[castcore]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[castcore]\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Please run as root (sudo)."

# Strict FFmpeg mode: abort if FFmpeg < 8.1.2 (CVE-2026-8461). Enable via the
# CASTCORE_REQUIRE_SAFE_FFMPEG=true env var or the --require-safe-ffmpeg flag.
REQUIRE_SAFE_FFMPEG="${CASTCORE_REQUIRE_SAFE_FFMPEG:-false}"
for arg in "$@"; do
  case "$arg" in
    --require-safe-ffmpeg) REQUIRE_SAFE_FFMPEG="true" ;;
  esac
done

# 1) OS check
. /etc/os-release 2>/dev/null || die "Cannot read /etc/os-release."
case "${ID}:${VERSION_ID:-}" in
  debian:12*|ubuntu:22.04|ubuntu:24.04) log "Detected ${PRETTY_NAME}." ;;
  debian:*|ubuntu:*) warn "Untested ${PRETTY_NAME}; continuing." ;;
  *) die "Unsupported OS: ${PRETTY_NAME}. Supported: Debian 12, Ubuntu LTS." ;;
esac

# 2) Packages (incl. FFmpeg/ffprobe, mount tooling, DB, cache)
log "Installing system packages…"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip \
  ffmpeg \
  postgresql redis-server \
  cifs-utils nfs-common rclone \
  git curl ca-certificates

command -v ffmpeg  >/dev/null || die "FFmpeg installation failed."
command -v ffprobe >/dev/null || die "ffprobe installation failed."

# FFmpeg security check (CVE-2026-8461 / "PixelSmash", MagicYUV decoder, fixed in 8.1.2).
# A vulnerable distro package is a warning, not a hard failure: CastCore still runs and warns
# at runtime, but operators should install a patched build (static build / backport).
FFMPEG_MIN="8.1.2"
ffver="$(ffmpeg -version 2>/dev/null | sed -nE 's/^ffmpeg version n?([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/p' | head -1)"
if [ -n "$ffver" ] && [ "$(printf '%s\n%s\n' "$FFMPEG_MIN" "$ffver" | sort -V | head -1)" != "$FFMPEG_MIN" ]; then
  if [ "$REQUIRE_SAFE_FFMPEG" = "true" ]; then
    die "FFmpeg ${ffver} is below ${FFMPEG_MIN} (CVE-2026-8461) and --require-safe-ffmpeg is set. Install a patched build (static/backport). See docs/admin-guide/ffmpeg-requirements."
  fi
  warn "FFmpeg ${ffver} is below ${FFMPEG_MIN} and may be affected by CVE-2026-8461 (MagicYUV)."
  warn "         Consider a patched static build or backport. See docs/admin-guide/ffmpeg-requirements."
elif [ -z "$ffver" ]; then
  if [ "$REQUIRE_SAFE_FFMPEG" = "true" ]; then
    die "Could not determine the FFmpeg version and --require-safe-ffmpeg is set; verify it is >= ${FFMPEG_MIN} (CVE-2026-8461)."
  fi
  warn "Could not determine the FFmpeg version; verify it is >= ${FFMPEG_MIN} (CVE-2026-8461)."
else
  log "FFmpeg ${ffver} OK (>= ${FFMPEG_MIN})."
fi

# 3) System user (no login shell)
if ! id "$APP_USER" >/dev/null 2>&1; then
  log "Creating system user '$APP_USER'…"
  useradd --system --home "$DATA_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi

# 4) Directories + permissions
log "Creating directories…"
mkdir -p "$APP_DIR" "$DATA_DIR"/{media,recordings,backups,mounts,thumbnails} "$LOG_DIR" "$ETC_DIR"
cp -r "$REPO_DIR"/backend "$REPO_DIR"/worker "$REPO_DIR"/process_manager "$APP_DIR"/
chown -R "$APP_USER:$APP_USER" "$APP_DIR" "$DATA_DIR" "$LOG_DIR"
chmod 750 "$DATA_DIR" "$LOG_DIR"

# 5) Python venv + dependencies
log "Setting up Python venv…"
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/venv/bin/pip" install --quiet "$APP_DIR/backend"
# worker/process_manager share the backend package; install their extras when present
[ -f "$APP_DIR/worker/requirements.txt" ] && "$APP_DIR/venv/bin/pip" install --quiet -r "$APP_DIR/worker/requirements.txt" || true

# 6) Environment file (secrets generated on first install)
if [ ! -f "$ETC_DIR/castcore.env" ]; then
  log "Generating $ETC_DIR/castcore.env with fresh secrets…"
  SECRET_KEY="$(openssl rand -hex 32)"
  ENCRYPTION_KEY="$("$APP_DIR/venv/bin/python" -c 'from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())')"
  DB_PASS="$(openssl rand -hex 16)"
  umask 077
  sed \
    -e "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" \
    -e "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=${ENCRYPTION_KEY}|" \
    -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${DB_PASS}|" \
    -e "s|^POSTGRES_HOST=.*|POSTGRES_HOST=localhost|" \
    -e "s|^REDIS_HOST=.*|REDIS_HOST=localhost|" \
    -e "s|^DATA_DIR=.*|DATA_DIR=${DATA_DIR}|" \
    -e "s|^MEDIA_DIR=.*|MEDIA_DIR=${DATA_DIR}/media|" \
    -e "s|^RECORDINGS_DIR=.*|RECORDINGS_DIR=${DATA_DIR}/recordings|" \
    -e "s|^LOG_DIR=.*|LOG_DIR=${LOG_DIR}|" \
    -e "s|^BACKUP_DIR=.*|BACKUP_DIR=${DATA_DIR}/backups|" \
    -e "s|^MOUNT_DIR=.*|MOUNT_DIR=${DATA_DIR}/mounts|" \
    -e "s|^THUMBNAIL_DIR=.*|THUMBNAIL_DIR=${DATA_DIR}/thumbnails|" \
    "$REPO_DIR/.env.example" > "$ETC_DIR/castcore.env"
  chown root:"$APP_USER" "$ETC_DIR/castcore.env"
  chmod 640 "$ETC_DIR/castcore.env"
else
  warn "$ETC_DIR/castcore.env already exists; leaving it untouched."
fi

# 7) PostgreSQL database/user
log "Configuring PostgreSQL…"
DB_PASS_LINE="$(grep '^POSTGRES_PASSWORD=' "$ETC_DIR/castcore.env" | cut -d= -f2-)"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='castcore'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER castcore WITH PASSWORD '${DB_PASS_LINE}';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='castcore'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE castcore OWNER castcore;"

# 8) DB migrations
log "Running database migrations…"
( cd "$APP_DIR/backend" && "$APP_DIR/venv/bin/alembic" upgrade head ) || \
  warn "Alembic migrations skipped/failed (no migrations yet in Phase 1 scaffold)."

# 9) systemd units
log "Installing systemd services…"
cp "$REPO_DIR"/deploy/systemd/castcore-*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now castcore-backend castcore-process-manager castcore-worker castcore-scheduler || \
  warn "Some services failed to start; check: journalctl -u castcore-backend"

log "Done. CastCore backend should listen on 127.0.0.1:8000."
log "Set up a reverse proxy (see deploy/caddy or deploy/nginx) for HTTPS, then open the Setup Wizard."

#!/usr/bin/env bash
# CastCore — native uninstaller. Stops services and removes the app.
# Data (database + /var/lib/castcore) is preserved unless --purge is given.
# Run as root: sudo ./scripts/uninstall.sh [--purge]
set -euo pipefail

APP_USER="castcore"
APP_DIR="/opt/castcore"
DATA_DIR="/var/lib/castcore"
LOG_DIR="/var/log/castcore"
ETC_DIR="/etc/castcore"
SERVICES="castcore-backend castcore-process-manager castcore-worker castcore-scheduler"
PURGE="${1:-}"

log()  { printf '\033[1;32m[castcore]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[castcore]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[castcore]\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Please run as root (sudo)."

log "Stopping and disabling services…"
systemctl disable --now $SERVICES 2>/dev/null || true
rm -f /etc/systemd/system/castcore-*.service
systemctl daemon-reload

log "Removing application directory…"
rm -rf "$APP_DIR"

if [ "$PURGE" = "--purge" ]; then
  warn "PURGE requested: this will DELETE all CastCore data, logs, config and the database."
  read -r -p "Type 'DELETE' to confirm: " confirm
  [ "$confirm" = "DELETE" ] || die "Aborted."
  rm -rf "$DATA_DIR" "$LOG_DIR" "$ETC_DIR"
  sudo -u postgres psql -c "DROP DATABASE IF EXISTS castcore;" || true
  sudo -u postgres psql -c "DROP USER IF EXISTS castcore;" || true
  userdel "$APP_USER" 2>/dev/null || true
  log "Purged all CastCore data."
else
  log "Data preserved at: $DATA_DIR (database kept). Re-run with --purge to remove everything."
fi

log "Uninstall complete."

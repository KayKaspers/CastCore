#!/usr/bin/env bash
# CastCore — native update: back up, pull, sync code, migrate, restart.
# Run as root: sudo ./scripts/update.sh
set -euo pipefail

APP_USER="castcore"
APP_DIR="/opt/castcore"
ETC_DIR="/etc/castcore"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES="castcore-backend castcore-process-manager castcore-worker castcore-scheduler"

log()  { printf '\033[1;32m[castcore]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[castcore]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[castcore]\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Please run as root (sudo)."

# 1) Backup first (strongly recommended before migrations)
log "Creating pre-update backup…"
"$APP_DIR/venv/bin/python" -m app.cli backup create --reason pre-update 2>/dev/null || \
  warn "Backup CLI not available yet (Phase 1 scaffold) — back up manually before production updates."

# 2) Pull latest code (if repo is a git checkout)
if [ -d "$REPO_DIR/.git" ]; then
  log "Pulling latest changes…"
  git -C "$REPO_DIR" pull --ff-only
fi

# 3) Sync code + dependencies
log "Syncing application code…"
systemctl stop $SERVICES || true
cp -r "$REPO_DIR"/backend "$REPO_DIR"/worker "$REPO_DIR"/process_manager "$APP_DIR"/
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
"$APP_DIR/venv/bin/pip" install --quiet --upgrade "$APP_DIR/backend"

# 4) Migrate
log "Applying database migrations…"
( cd "$APP_DIR/backend" && "$APP_DIR/venv/bin/alembic" upgrade head ) || \
  die "Migration failed. Restore the pre-update backup and investigate before retrying."

# 5) Restart
log "Restarting services…"
systemctl start $SERVICES
log "Update complete. Verify: systemctl status castcore-backend"

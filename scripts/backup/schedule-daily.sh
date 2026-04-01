#!/usr/bin/env bash
# Install a daily cron job for Galley Archive backup.
#
# Default schedule: 02:30 every day.
# Override with GALLEY_CRON_HOUR and GALLEY_CRON_MINUTE env vars.
#
# Usage:
#   bash scripts/backup/schedule-daily.sh          # install/update
#   bash scripts/backup/schedule-daily.sh remove   # remove the cron entry
#
# The cron entry writes its own log to data/logs/backup-cron.log.
# Run  make backup-list  to confirm backups are being created.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

BACKUP_SCRIPT="$REPO_ROOT/scripts/backup/backup.sh"
LOG_FILE="$REPO_ROOT/data/logs/backup-cron.log"
CRON_HOUR="${GALLEY_CRON_HOUR:-2}"
CRON_MINUTE="${GALLEY_CRON_MINUTE:-30}"
CRON_MARKER="# galley-archive-backup"

CRON_LINE="$CRON_MINUTE $CRON_HOUR * * * bash $BACKUP_SCRIPT >> $LOG_FILE 2>&1 $CRON_MARKER"

if [ "${1:-}" = "remove" ]; then
    if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
        crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | crontab -
        echo "Galley backup cron entry removed."
    else
        echo "No Galley backup cron entry found — nothing to remove."
    fi
    exit 0
fi

# Ensure log directory exists
mkdir -p "$REPO_ROOT/data/logs"

# Install or update
existing=$(crontab -l 2>/dev/null || true)
if echo "$existing" | grep -q "$CRON_MARKER"; then
    # Replace existing entry
    updated=$(echo "$existing" | grep -v "$CRON_MARKER")
    (echo "$updated"; echo "$CRON_LINE") | crontab -
    echo "Updated existing Galley backup cron entry."
else
    # Append new entry
    (echo "$existing"; echo "$CRON_LINE") | crontab -
    echo "Installed Galley backup cron entry."
fi

echo ""
echo "Schedule: daily at ${CRON_HOUR}:$(printf '%02d' "$CRON_MINUTE") (local time)"
echo "Log file: $LOG_FILE"
echo ""
echo "Current cron entry:"
crontab -l | grep "$CRON_MARKER"
echo ""
echo "To remove: bash scripts/backup/schedule-daily.sh remove"
echo "To list backups: make backup-list"

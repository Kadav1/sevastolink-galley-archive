#!/usr/bin/env bash
# restore.sh — restore Galley Archive data from a backup directory
#
# Usage:
#   bash scripts/backup/restore.sh data/backups/galley-YYYYMMDD-HHMMSS
#   make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
#
# What is restored (only items present in the backup):
#   galley.sqlite   → data/db/galley.sqlite
#   media/          → data/media/
#   imports/        → data/imports/
#
# Safety rules:
#   - Requires an explicit backup path argument
#   - Shows what will be overwritten before doing anything
#   - Requires interactive confirmation unless GALLEY_RESTORE_YES=1 is set
#   - Stops if the backup directory does not exist
#   - Does NOT restore .env — review env.bak manually if needed
#
# Recommendation: stop the application before restoring the database.
#   make down
#   make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
#   make up

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

BACKUP_DIR="${1:-}"

# ── Argument check ────────────────────────────────────────────────────────────

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: bash scripts/backup/restore.sh <backup-dir>"
    echo "       make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS"
    echo ""
    echo "Available backups:"
    ls -1t data/backups/ 2>/dev/null | grep -v '^\.' || echo "  (none)"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: backup directory not found: $BACKUP_DIR"
    echo ""
    echo "Available backups:"
    ls -1t data/backups/ 2>/dev/null | grep -v '^\.' || echo "  (none)"
    exit 1
fi

# ── Inventory what the backup contains ───────────────────────────────────────

HAS_DB=0
HAS_MEDIA=0
HAS_IMPORTS=0

[ -f "$BACKUP_DIR/galley.sqlite" ] && HAS_DB=1
[ -d "$BACKUP_DIR/media" ]         && HAS_MEDIA=1
[ -d "$BACKUP_DIR/imports" ]       && HAS_IMPORTS=1

if [ "$HAS_DB" -eq 0 ] && [ "$HAS_MEDIA" -eq 0 ] && [ "$HAS_IMPORTS" -eq 0 ]; then
    echo "Error: backup at $BACKUP_DIR contains no restorable items."
    echo "Expected galley.sqlite, media/, or imports/ inside the backup directory."
    exit 1
fi

# ── Show plan ────────────────────────────────────────────────────────────────

echo "Galley Archive restore"
echo "Source: $BACKUP_DIR"
echo ""

if [ -f "$BACKUP_DIR/BACKUP_INFO.txt" ]; then
    echo "Backup info:"
    grep -E "^(Created|Hostname):" "$BACKUP_DIR/BACKUP_INFO.txt" | sed 's/^/  /'
    echo ""
fi

echo "This will overwrite:"
[ "$HAS_DB" -eq 1 ]      && echo "  data/db/galley.sqlite"
[ "$HAS_MEDIA" -eq 1 ]   && echo "  data/media/"
[ "$HAS_IMPORTS" -eq 1 ] && echo "  data/imports/"
echo ""

# Check for existing data that would be overwritten
WARN=0
[ "$HAS_DB" -eq 1 ] && [ -f "data/db/galley.sqlite" ] && WARN=1
[ "$HAS_MEDIA" -eq 1 ] && [ -d "data/media" ] && [ -n "$(ls -A data/media 2>/dev/null)" ] && WARN=1
[ "$HAS_IMPORTS" -eq 1 ] && [ -d "data/imports" ] && [ -n "$(ls -A data/imports 2>/dev/null)" ] && WARN=1

if [ "$WARN" -eq 1 ]; then
    echo "Warning: existing data will be replaced. This cannot be undone."
    echo "Run 'make backup' first if you want to preserve the current state."
    echo ""
fi

# ── Confirmation ──────────────────────────────────────────────────────────────

if [ "${GALLEY_RESTORE_YES:-0}" != "1" ]; then
    read -r -p "Continue with restore? [y/N] " confirm
    case "$confirm" in
        [yY]) ;;
        *) echo "Restore cancelled."; exit 0 ;;
    esac
    echo ""
fi

# ── Restore ───────────────────────────────────────────────────────────────────

if [ "$HAS_DB" -eq 1 ]; then
    mkdir -p data/db
    cp "$BACKUP_DIR/galley.sqlite" data/db/galley.sqlite
    echo "  [ok] database restored"
fi

if [ "$HAS_MEDIA" -eq 1 ]; then
    rm -rf data/media
    cp -r "$BACKUP_DIR/media" data/media
    echo "  [ok] media restored"
fi

if [ "$HAS_IMPORTS" -eq 1 ]; then
    rm -rf data/imports
    cp -r "$BACKUP_DIR/imports" data/imports
    echo "  [ok] imports restored"
fi

echo ""
echo "Restore complete from: $BACKUP_DIR"

if [ "${GALLEY_RUNNING:-0}" = "1" ] || docker compose ps 2>/dev/null | grep -q "running"; then
    echo ""
    echo "Note: the application appears to be running. Restart it to use the restored data:"
    echo "  make restart"
fi

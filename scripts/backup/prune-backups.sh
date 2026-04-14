#!/usr/bin/env bash
# prune-backups.sh — remove old Galley Archive backups, keeping the N most recent.
#
# Usage:
#   bash scripts/backup/prune-backups.sh [KEEP]
#
#   KEEP — number of backups to retain (default: 7)
#
# Backup directories are named galley-YYYYMMDD-HHMMSS (produced by backup.sh).
# Age is determined by parsing the name timestamp, NOT filesystem mtime,
# so the sort order is stable even if files are copied or rsync'd.
#
# Only directories matching galley-[0-9]{8}-[0-9]{6} are considered.
# Other contents of the backup base directory are left untouched.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

BACKUP_BASE="${GALLEY_BACKUP_DIR:-data/backups}"
KEEP="${1:-7}"

# Validate KEEP is a positive integer
if ! [[ "$KEEP" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: KEEP must be a positive integer (got: $KEEP)" >&2
    exit 1
fi

if [ ! -d "$BACKUP_BASE" ]; then
    echo "Backup directory not found: $BACKUP_BASE — nothing to prune."
    exit 0
fi

# Collect backup directories whose names match the expected pattern.
# Sort descending by name (most recent first) — YYYYMMDD-HHMMSS sorts lexicographically.
mapfile -t ALL_BACKUPS < <(
    find "$BACKUP_BASE" -mindepth 1 -maxdepth 1 -type d \
        -regextype posix-extended \
        -regex '.*/galley-[0-9]{8}-[0-9]{6}' \
        -printf '%f\n' \
    | sort -r
)

TOTAL="${#ALL_BACKUPS[@]}"

if [ "$TOTAL" -eq 0 ]; then
    echo "No backups found in $BACKUP_BASE — nothing to prune."
    exit 0
fi

echo "Galley Archive backup prune"
echo "Backup dir:  $BACKUP_BASE"
echo "Total found: $TOTAL"
echo "Keeping:     $KEEP"
echo ""

if [ "$TOTAL" -le "$KEEP" ]; then
    echo "Nothing to remove (have $TOTAL, keeping $KEEP)."
    exit 0
fi

# Everything after index KEEP-1 is to be removed
REMOVE=("${ALL_BACKUPS[@]:$KEEP}")

for name in "${REMOVE[@]}"; do
    target="$BACKUP_BASE/$name"
    echo "  Removing: $target"
    rm -rf "$target"
done

echo ""
echo "Pruned $((TOTAL - KEEP)) backup(s). $KEEP retained."

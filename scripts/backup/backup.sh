#!/usr/bin/env bash
# backup.sh — create a timestamped backup of Galley Archive data
#
# Usage:
#   bash scripts/backup/backup.sh
#   make backup
#
# What is backed up:
#   data/db/galley.sqlite   — recipe database (online backup via sqlite3 or cp)
#   data/media/             — uploaded media assets
#   data/imports/           — raw source files
#   .env                    — config snapshot (reference only, not for restore)
#
# Output: data/backups/galley-YYYYMMDD-HHMMSS/
#
# Notes:
#   - Run from the repo root
#   - The backup is a plain directory — inspect it with ls/find
#   - For the safest database backup, stop the API first (make down)
#     or ensure SQLite WAL mode is not in a mid-transaction state.
#     sqlite3 .backup is used when sqlite3 is available; it is safe
#     for running databases. cp is used as fallback and may be unsafe
#     if the database has an active write transaction.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

BACKUP_BASE="${GALLEY_BACKUP_DIR:-data/backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$BACKUP_BASE/galley-$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

echo "Galley Archive backup"
echo "Destination: $BACKUP_DIR"
echo ""

# ── Database ──────────────────────────────────────────────────────────────────

DB_PATH="${GALLEY_DB_PATH:-data/db/galley.sqlite}"

if [ -f "$DB_PATH" ]; then
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/galley.sqlite'"
        echo "  [ok] database (sqlite3 online backup)"
    else
        cp "$DB_PATH" "$BACKUP_DIR/galley.sqlite"
        echo "  [ok] database (cp — sqlite3 not found; stop the API for safest results)"
    fi
else
    echo "  [skip] database — not found at $DB_PATH"
fi

# ── Media ─────────────────────────────────────────────────────────────────────

if [ "${GALLEY_SKIP_MEDIA:-0}" = "1" ]; then
    echo "  [skip] media (GALLEY_SKIP_MEDIA)"
elif [ -d "data/media" ] && [ -n "$(ls -A data/media 2>/dev/null)" ]; then
    cp -r data/media "$BACKUP_DIR/media"
    echo "  [ok] media"
elif [ -d "data/media" ]; then
    mkdir -p "$BACKUP_DIR/media"
    echo "  [ok] media (empty)"
else
    echo "  [skip] media — directory not found"
fi

# ── Imports ───────────────────────────────────────────────────────────────────

if [ "${GALLEY_SKIP_IMPORTS:-0}" = "1" ]; then
    echo "  [skip] imports (GALLEY_SKIP_IMPORTS)"
elif [ -d "data/imports" ] && [ -n "$(ls -A data/imports 2>/dev/null)" ]; then
    cp -r data/imports "$BACKUP_DIR/imports"
    echo "  [ok] imports"
elif [ -d "data/imports" ]; then
    mkdir -p "$BACKUP_DIR/imports"
    echo "  [ok] imports (empty)"
else
    echo "  [skip] imports — directory not found"
fi

# ── Config reference ──────────────────────────────────────────────────────────

if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/env.bak"
    echo "  [ok] .env snapshot (reference — not used by restore)"
else
    echo "  [skip] .env — not found"
fi

# ── Manifest ──────────────────────────────────────────────────────────────────

cat > "$BACKUP_DIR/BACKUP_INFO.txt" <<EOF
Galley Archive backup
Created:  $(date -Iseconds)
Hostname: $(hostname)
Source:   $REPO_ROOT

Contents:
$(find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 | sort)
EOF

echo ""
echo "Backup complete: $BACKUP_DIR"

#!/usr/bin/env bash
# rollback-migration.sh — roll back the most recently applied Galley migration.
#
# Usage:
#   bash scripts/db/rollback-migration.sh [VERSION]
#
#   VERSION — optional migration version to roll back (e.g. "004").
#             Defaults to the most recently applied migration.
#
# What it does:
#   1. Looks up the target version in schema_migrations.
#   2. Executes the corresponding <version>_*.rollback.sql file.
#   3. Removes the version row from schema_migrations.
#
# Prerequisites:
#   - sqlite3 must be available on PATH.
#   - Take a backup first: bash scripts/backup/backup.sh
#
# Notes:
#   - Rollbacks run outside a savepoint because executescript() in SQLite
#     implicitly commits. The rollback SQL itself is the unit of work.
#   - For migration 001 (initial schema), ALL data is destroyed.
#     There is no recovery — take a backup first.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

DB_PATH="${GALLEY_DB_PATH:-data/db/galley.sqlite}"
MIGRATIONS_DIR="apps/api/src/db/migrations"

if ! command -v sqlite3 >/dev/null 2>&1; then
    echo "Error: sqlite3 not found on PATH." >&2
    exit 1
fi

if [ ! -f "$DB_PATH" ]; then
    echo "Error: database not found at $DB_PATH" >&2
    exit 1
fi

# Determine target version
if [ -n "${1:-}" ]; then
    TARGET_VERSION="$1"
else
    TARGET_VERSION="$(
        sqlite3 "$DB_PATH" \
            "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;"
    )"
fi

if [ -z "$TARGET_VERSION" ]; then
    echo "No migrations found in schema_migrations — nothing to roll back."
    exit 0
fi

# Find the matching rollback file
ROLLBACK_FILE="$(
    find "$MIGRATIONS_DIR" -name "${TARGET_VERSION}_*.rollback.sql" | sort | head -1
)"

if [ -z "$ROLLBACK_FILE" ]; then
    echo "Error: no rollback file found for version $TARGET_VERSION in $MIGRATIONS_DIR" >&2
    exit 1
fi

echo "Galley Archive migration rollback"
echo "Version:  $TARGET_VERSION"
echo "Script:   $ROLLBACK_FILE"
echo "Database: $DB_PATH"
echo ""
echo "WARNING: This operation may destroy data. Take a backup first."
echo "         bash scripts/backup/backup.sh"
echo ""

read -r -p "Proceed? [y/N] " confirm
if [[ "${confirm,,}" != "y" ]]; then
    echo "Aborted."
    exit 0
fi

# Apply rollback SQL
sqlite3 "$DB_PATH" < "$ROLLBACK_FILE"

# Remove from schema_migrations
sqlite3 "$DB_PATH" \
    "DELETE FROM schema_migrations WHERE version = '$TARGET_VERSION';"

echo ""
echo "Rollback complete. Migration $TARGET_VERSION has been removed."

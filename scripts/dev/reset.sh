#!/usr/bin/env bash
# Reset the dev database: drop the SQLite file, re-run migrations, and seed.
# WARNING: destroys all local data. Never run against a backup you care about.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
API_DIR="$REPO_ROOT/apps/api"
DB_PATH="$REPO_ROOT/data/db/galley.sqlite"

echo "This will DELETE $DB_PATH and reseed from scratch."
read -rp "Continue? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

if [ -f "$DB_PATH" ]; then
  rm "$DB_PATH"
  echo "Removed $DB_PATH"
fi

cd "$API_DIR"

echo ""
echo "Running migrations..."
python -c "
import sys
sys.path.insert(0, '.')
from src.db.init_db import init_db
init_db()
"

echo ""
echo "Seeding dev fixtures..."
python "$REPO_ROOT/scripts/seed/seed_dev.py"

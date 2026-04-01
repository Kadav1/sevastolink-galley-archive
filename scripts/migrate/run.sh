#!/usr/bin/env bash
# Run all pending database migrations.
# Must be executed from the repo root or apps/api/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
API_DIR="$REPO_ROOT/apps/api"

if [ ! -f "$API_DIR/src/db/init_db.py" ]; then
  echo "Error: run from repo root or apps/api/" >&2
  exit 1
fi

cd "$API_DIR"

echo "Running migrations..."
python -c "
import sys
sys.path.insert(0, '.')
from src.db.init_db import init_db
init_db()
print('Migrations complete.')
"

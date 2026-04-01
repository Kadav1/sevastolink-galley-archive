#!/usr/bin/env bash
# Dev environment check — verifies prerequisites before first run.
# Safe to run repeatedly. Exits non-zero if any required check fails.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PASS=0
FAIL=0

ok()   { echo "  ok   $1"; ((PASS++)) || true; }
fail() { echo "  FAIL $1"; ((FAIL++)) || true; }
info() { echo "       $1"; }

echo "Galley Archive — dev environment check"
echo ""

# ── Python ────────────────────────────────────────────────────────────────────

echo "Python"
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; exit(0 if sys.version_info >= (3,12) else 1)"; then
        ok "python $PY_VER (>= 3.12 required)"
    else
        fail "python $PY_VER — 3.12+ required"
    fi
else
    fail "python3 not found"
fi

# ── API deps ──────────────────────────────────────────────────────────────────

echo ""
echo "API dependencies (apps/api)"
cd "$REPO_ROOT/apps/api"
for pkg in fastapi uvicorn pydantic sqlalchemy httpx pytest; do
    if python3 -c "import $pkg" 2>/dev/null; then
        ok "$pkg"
    else
        fail "$pkg not installed — run: pip install -e '.[dev]' from apps/api/"
    fi
done

# ── Node ──────────────────────────────────────────────────────────────────────

echo ""
echo "Node / npm (apps/web)"
cd "$REPO_ROOT"
if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    if node -e "process.exit(parseInt(process.version.slice(1)) >= 20 ? 0 : 1)"; then
        ok "node $NODE_VER (>= 20 required)"
    else
        fail "node $NODE_VER — 20+ required"
    fi
else
    fail "node not found"
fi

if command -v npm &>/dev/null; then
    ok "npm $(npm --version)"
else
    fail "npm not found"
fi

if [ -d "$REPO_ROOT/apps/web/node_modules" ]; then
    ok "apps/web node_modules present"
else
    fail "apps/web/node_modules missing — run: npm install from apps/web/"
fi

# ── Environment config ────────────────────────────────────────────────────────

echo ""
echo "Environment"
if [ -f "$REPO_ROOT/.env" ]; then
    ok ".env present"
else
    fail ".env not found — run: cp .env.example .env"
fi

# ── Data directories ──────────────────────────────────────────────────────────

echo ""
echo "Data directories"
for dir in data/db data/media data/imports data/exports data/backups data/logs; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        ok "$dir"
    else
        fail "$dir missing — run: make init-data"
    fi
done

# ── Docker (optional) ─────────────────────────────────────────────────────────

echo ""
echo "Docker (optional — only needed for 'make up')"
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    ok "docker running"
elif command -v docker &>/dev/null; then
    info "docker installed but daemon not running"
else
    info "docker not found (install Docker Desktop to use 'make up')"
fi

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "────────────────────────────────"
if [ "$FAIL" -eq 0 ]; then
    echo "All checks passed ($PASS ok)"
    exit 0
else
    echo "$FAIL check(s) failed — fix the issues above before running the app"
    exit 1
fi

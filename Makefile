.PHONY: help up up-detach up-proxy down restart logs logs-api logs-web logs-nginx ps build rebuild \
        shell-api shell-web \
        init-data test-api test-api-v test-api-q test-api-k \
        secrets-scan install-git-hooks \
        backup backup-db backup-list restore backup-prune \
        dev-check seed-dev install-api install-web dev-api dev-web build-web \
        clean tree

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo "Sevastolink Galley Archive"
	@echo ""
	@echo "Run:"
	@echo "  make up              Build images and start services (foreground)"
	@echo "  make up-detach       Start in background"
	@echo "  make up-proxy        Start with nginx reverse proxy on port 8080"
	@echo "  make down            Stop all services"
	@echo "  make restart         Restart all services"
	@echo ""
	@echo "Observe:"
	@echo "  make logs            Tail all logs"
	@echo "  make logs-api        Tail API logs"
	@echo "  make logs-web        Tail web logs"
	@echo "  make logs-nginx      Tail nginx logs (requires up-proxy)"
	@echo "  make ps              Show running containers"
	@echo ""
	@echo "Build:"
	@echo "  make build           Build images without starting"
	@echo "  make rebuild         Build with no cache"
	@echo ""
	@echo "Shell:"
	@echo "  make shell-api       Shell inside API container"
	@echo "  make shell-web       Shell inside web container"
	@echo ""
	@echo "Data:"
	@echo "  make init-data       Create data directories (safe to repeat)"
	@echo "  make backup          Create timestamped backup under data/backups/"
	@echo "  make backup-db       Database-only backup (skips media/imports)"
	@echo "  make backup-list     List available backups"
	@echo "  make backup-prune    Keep the N most recent backups (KEEP=7)"
	@echo "  make restore BACKUP=<path>  Restore from a backup directory"
	@echo ""
	@echo "Tests:"
	@echo "  make test-api        Run API tests (standard output)"
	@echo "  make test-api-v      Run API tests (verbose)"
	@echo "  make test-api-q      Run API tests (quiet: dots only)"
	@echo "  make test-api-k K=x  Run tests matching keyword x"
	@echo "  make secrets-scan    Scan the repo for high-confidence hardcoded secrets"
	@echo ""
	@echo "Dev:"
	@echo "  make install-api     Install API dependencies into the repo .venv"
	@echo "  make install-web     Install web dependencies"
	@echo "  make dev-api         Run the FastAPI app locally from apps/api"
	@echo "  make dev-web         Run the Vite dev server locally from apps/web"
	@echo "  make build-web       Build the frontend from apps/web"
	@echo "  make dev-check       Verify dev environment prerequisites"
	@echo "  make seed-dev        Insert fixture recipes into dev database"
	@echo "  make install-git-hooks  Install the local pre-commit secret scan hook"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove containers, images (does NOT touch data/)"

# ── Compose lifecycle ─────────────────────────────────────────────────────────

up: init-data
	docker compose up --build

up-detach: init-data
	docker compose up --build -d

# Start with nginx reverse proxy on port 8080 (configured via NGINX_PORT in .env)
up-proxy: init-data
	docker compose --profile proxy up --build

up-proxy-detach: init-data
	docker compose --profile proxy up --build -d

down:
	docker compose down

restart:
	docker compose restart

# ── Observability ─────────────────────────────────────────────────────────────

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f galley-api

logs-web:
	docker compose logs -f galley-web

logs-nginx:
	docker compose --profile proxy logs -f galley-nginx

ps:
	docker compose ps

# ── Builds ────────────────────────────────────────────────────────────────────

build:
	docker compose build

rebuild:
	docker compose build --no-cache

# ── Shell access ──────────────────────────────────────────────────────────────

shell-api:
	docker compose exec galley-api bash

shell-web:
	docker compose exec galley-web sh

# ── Data directories ─────────────────────────────────────────────────────────
# Creates host-side data dirs bind-mounted into the API container.
# Safe to run multiple times; called automatically by `up`.

init-data:
	mkdir -p data/db data/media data/imports data/exports data/backups data/logs

# ── Backup and restore ────────────────────────────────────────────────────────

backup: init-data
	@bash scripts/backup/backup.sh

# Database-only backup — faster than full backup when media is unchanged
backup-db: init-data
	@GALLEY_SKIP_MEDIA=1 GALLEY_SKIP_IMPORTS=1 bash scripts/backup/backup.sh

backup-list:
	@echo "Available backups in data/backups/:"
	@ls -1t data/backups/ 2>/dev/null | grep -v '^\.' || echo "  (none)"

# BACKUP variable must be supplied: make restore BACKUP=data/backups/galley-20260326-120000
restore:
	@if [ -z "$(BACKUP)" ]; then \
	    echo "Error: specify backup path — make restore BACKUP=data/backups/galley-<timestamp>"; \
	    exit 1; \
	fi
	@bash scripts/backup/restore.sh "$(BACKUP)"

# Keep the N most recent backups; remove the rest.
# Age is determined by parsing the backup directory name (YYYYMMDD-HHMMSS),
# not filesystem mtime — so sort order is stable across copies and restores.
# Usage: make backup-prune or make backup-prune KEEP=14
KEEP ?= 7
backup-prune:
	@bash scripts/backup/prune-backups.sh "$(KEEP)"

# ── Tests ─────────────────────────────────────────────────────────────────────

test-api:
	cd apps/api && python -m pytest

test-api-v:
	cd apps/api && python -m pytest -v

# Quiet: dots only, no captured output
test-api-q:
	cd apps/api && python -m pytest -q

# Run tests matching a keyword: make test-api-k K=intake
test-api-k:
	cd apps/api && python -m pytest -k "$(K)" -v

secrets-scan:
	bash scripts/dev/scan_secrets.sh

install-git-hooks:
	bash scripts/dev/install_git_hooks.sh

install-api:
	@if [ ! -x ".venv/bin/python" ]; then \
	    echo "Error: .venv/bin/python not found. Create the repo virtualenv first, e.g. python3 -m venv .venv"; \
	    exit 1; \
	fi
	.venv/bin/pip install -e packages/shared-prompts
	cd apps/api && ../../.venv/bin/python -m pip install -e ".[dev]"

install-web:
	@if ! command -v npm >/dev/null 2>&1; then \
	    echo "Error: npm not found. Install Node.js 20+ and npm first."; \
	    exit 1; \
	fi
	cd apps/web && npm install

dev-api:
	@if [ ! -x ".venv/bin/python" ]; then \
	    echo "Error: .venv/bin/python not found. Run 'make install-api' after creating the repo virtualenv."; \
	    exit 1; \
	fi
	@if ! .venv/bin/python -c "import uvicorn, fastapi" >/dev/null 2>&1; then \
	    echo "Error: API dependencies are not installed in .venv. Run 'make install-api' first."; \
	    exit 1; \
	fi
	cd apps/api && ../../.venv/bin/python -m uvicorn src.main:app --reload --port 8000

dev-web:
	@if [ ! -d "apps/web/node_modules" ]; then \
	    echo "Error: apps/web/node_modules is missing. Run 'make install-web' first."; \
	    exit 1; \
	fi
	cd apps/web && npm run dev

build-web:
	@if [ ! -d "apps/web/node_modules" ]; then \
	    echo "Error: apps/web/node_modules is missing. Run 'make install-web' first."; \
	    exit 1; \
	fi
	cd apps/web && npm run build

# ── Cleanup ───────────────────────────────────────────────────────────────────
# Removes containers and images only. Data in data/ is NOT touched.

# ── Dev helpers ───────────────────────────────────────────────────────────────

# Verify prerequisites (Python, Node, .env, data dirs, optional Docker)
dev-check:
	@bash scripts/dev/check.sh

# Insert dev fixture recipes (idempotent — skips existing slugs)
seed-dev:
	cd apps/api && python ../../scripts/seed/seed_dev.py

clean:
	docker compose down --volumes --remove-orphans
	docker image rm galley-api galley-web 2>/dev/null || true

# ── Utility ───────────────────────────────────────────────────────────────────

tree:
	find . -maxdepth 4 | sort

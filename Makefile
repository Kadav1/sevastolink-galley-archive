.PHONY: help up up-detach up-proxy down restart logs logs-api logs-web logs-nginx ps build rebuild \
        shell-api shell-web \
        init-data test-api test-api-v test-api-q test-api-k \
        backup backup-db backup-list restore backup-prune \
        dev-check seed-dev \
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
	@echo "  make backup-prune    Remove backups older than 30 days (KEEP_DAYS=N)"
	@echo "  make restore BACKUP=<path>  Restore from a backup directory"
	@echo ""
	@echo "Tests:"
	@echo "  make test-api        Run API tests (standard output)"
	@echo "  make test-api-v      Run API tests (verbose)"
	@echo "  make test-api-q      Run API tests (quiet: dots only)"
	@echo "  make test-api-k K=x  Run tests matching keyword x"
	@echo ""
	@echo "Dev:"
	@echo "  make dev-check       Verify dev environment prerequisites"
	@echo "  make seed-dev        Insert fixture recipes into dev database"
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

# Remove backups older than N days. Defaults to 30 days.
# Usage: make backup-prune or make backup-prune KEEP_DAYS=14
KEEP_DAYS ?= 30
backup-prune:
	@echo "Pruning backups older than $(KEEP_DAYS) days from data/backups/..."; \
	find data/backups/ -maxdepth 1 -type d -name 'galley-*' -mtime +$(KEEP_DAYS) -print -exec rm -rf {} + ; \
	echo "Done."

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

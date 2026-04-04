# Sevastolink Galley Archive

Sevastolink Galley Archive is a local-first, self-hosted recipe archive and cooking workspace. It runs as a FastAPI + React application, keeps its data on your machine, is designed for practical kitchen use, and can optionally use LM Studio for structured AI-assisted intake and retrieval tasks.

It is `archive-first`: recipe records, source evidence, trust state, and refinement remain the system core. Pantry and AI features support the archive rather than replacing it.

## At A Glance

- local-first and self-hosted
- usable today for archive browsing, intake, kitchen use, pantry suggestion, and CLI-assisted bulk import
- optional LM Studio integration; core archive workflows work without AI
- broader target-state specs live under `docs/`, but they describe more than is currently shipped

If you need implementation truth, start with:

- `docs/00_overview/current-state.md`
- `docs/01_product/implemented-product.md`
- `docs/02_ux/implemented-routes-and-flows.md`
- `docs/07_api/implemented-api.md`

## What Works Today

Current web product:

- library at `/` and `/library`
- recipe detail at `/recipe/:slug`
- kitchen mode at `/recipe/:slug/kitchen`
- pantry workspace at `/pantry`
- intake hub at `/intake`
- manual entry at `/intake/manual`
- paste-text intake at `/intake/paste`
- settings shell at `/settings` (placeholder)

Current AI-backed product surfaces:

- paste-text normalization and evaluation during intake
- recipe detail AI tools for metadata suggestion, rewrite, and similar recipes
- pantry suggestion workspace

Current local tooling:

- Docker-based local deployment
- optional nginx reverse proxy
- file-based backup and restore
- CLI importer that normalizes raw recipe sources into candidate bundles
- CLI review, patch, ingest, and approval workflow for backlog imports

Not fully shipped yet:

- URL intake in the routed web UI
- file or image intake in the routed web UI
- dedicated AI tools route group
- full settings UI
- broader library route surfaces such as favorites, recent, verified, and drafts

## For Self-Hosters

### Quick Start

Recommended local run path:

```bash
cp .env.example .env
make up
```

Default local addresses:

- Web UI: `http://localhost:3000`
- API health: `http://localhost:8000/api/health`

`make up` creates the required `data/` directories before starting the stack.

For deployment details, reverse proxy setup, and systemd support, see:

- `docs/09_ops/local-deployment.md`
- `docs/09_ops/implemented-ops.md`
- `docs/09_ops/backup-restore.md`

### Core Operations

Stack lifecycle:

```bash
make up
make up-detach
make up-proxy
make up-proxy-detach
make down
make restart
```

Logs and shells:

```bash
make logs
make logs-api
make logs-web
make logs-nginx
make shell-api
make shell-web
make ps
```

Backup and restore:

```bash
make backup
make backup-db
make backup-list
make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
make backup-prune
```

### Optional LM Studio

LM Studio is optional and runs outside Docker on your host machine. Core archive behavior does not depend on it.

To enable AI features:

1. Start LM Studio and load a model.
2. Set the relevant values in `.env`:

```env
LM_STUDIO_ENABLED=true
LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
LM_STUDIO_MODEL=<your-model-name>
```

3. Restart the app:

```bash
make restart
```

If LM Studio is unavailable, AI-assisted features fail gracefully and the rest of the archive continues to work.

### Bulk Import Workflow

The routed web UI covers one-at-a-time intake. For backlog imports, use the CLI workflow.

Place raw source files under `data/imports/raw/recipes/`, then generate candidate bundles:

```bash
python3 scripts/import/normalize_recipes.py \
  --file 'data/imports/raw/recipes/Example.md' \
  data/imports/parsed/recipes-candidates \
  --model "Qwen/Qwen2.5-7B-Instruct"
```

Review candidates:

```bash
python3 scripts/import/review_candidates.py list
python3 scripts/import/review_candidates.py show \
  'data/imports/parsed/recipes-candidates/Example.candidate.json'
```

Approve reviewed candidates:

```bash
python3 scripts/import/review_candidates.py approve \
  'data/imports/parsed/recipes-candidates/Example.candidate.json'
```

Important rule: treat raw source files as preserved evidence. Do not edit them in place after intake.

For the full importer workflow, staged preprocessing details, and review rules, see:

- `docs/10_imports/recipe-import-workflow.md`

## For Contributors

### Local Development Without Docker

```bash
# One-time setup
python3 -m venv .venv
make install-api
make install-web

# Run in separate terminals
make dev-api
make dev-web
```

### Build And Test

```bash
make test-api
make build-web

cd apps/api && python -m pytest -v
cd apps/web && npm run build
```

### Secret Scanning

Run the repo-standard secret scan:

```bash
make secrets-scan
```

To install the optional local pre-commit hook that runs the same scan before commits:

```bash
make install-git-hooks
```

### Repository Layout

```text
apps/
  api/         FastAPI backend, models, services, migrations, tests
  web/         Vite/React frontend
packages/
  shared-types/
  shared-ui-tokens/
  shared-taxonomy/
  shared-prompts/
docs/          product, UX, API, schema, ops, and implementation-aware docs
prompts/       runtime and schema prompt assets
scripts/       backup, import, migration, and seed tooling
data/          local runtime data and import artifacts
```

### Documentation Map

Implementation-aware docs:

- `docs/00_overview/current-state.md`
- `docs/01_product/implemented-product.md`
- `docs/02_ux/implemented-routes-and-flows.md`
- `docs/05_ai/implemented-ai.md`
- `docs/07_api/implemented-api.md`
- `docs/09_ops/implemented-ops.md`

Broader target-state docs:

- `docs/01_product/product-brief.md`
- `docs/02_ux/information-architecture.md`
- `docs/02_ux/implementation-backlog.md`
- `docs/05_ai/ai-interaction-spec.md`

Rule of thumb:

- use `implemented-*` and `current-state.md` when you need to know what is true in the repo now
- use broader specs when you need product direction or target-state intent
- do not document a spec-only route or workflow as shipped behavior

## Persistent Data

Persistent runtime data lives under `data/`:

```text
data/
├── backups/   timestamped backup snapshots
├── db/        SQLite database
├── exports/   exported archive artifacts
├── imports/   raw and parsed intake/import files
├── logs/      local logs
└── media/     uploaded media assets
```

`make clean` removes containers and images only. It does not remove `data/`.

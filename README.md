# Sevastolink Galley Archive

Sevastolink Galley Archive is a local-first recipe archive and cooking workspace. It runs as a self-hosted FastAPI + React application, keeps its data on your machine, supports practical kitchen use, and can optionally use LM Studio for a semantics-first staged import pipeline during intake.

The current product is already usable for:

- browsing a recipe library
- viewing recipe detail
- cooking from a focused kitchen-mode route
- creating recipes manually
- pasting raw recipe text and turning it into structured archive records
- bulk-importing recipe source files through CLI review workflows

This repository also contains broader target-state specs under `docs/`. Those specs describe more than is currently shipped. When you need to know what actually works today, use the implementation-aware docs listed below.

## What Is Implemented Now

Current web product:

- library landing at `/` and `/library`
- recipe detail at `/recipe/:slug`
- kitchen mode at `/recipe/:slug/kitchen`
- pantry workspace at `/pantry`
- intake hub at `/intake`
- manual entry at `/intake/manual`
- paste-text intake with optional AI normalization at `/intake/paste`
- settings route shell at `/settings` (placeholder)

Current backend/API:

- health endpoint at `/api/health`
- recipe endpoints under `/api/v1/recipes`
- intake endpoints under `/api/v1/intake-jobs`
- pantry suggestion endpoint under `/api/v1/pantry`
- settings endpoint under `/api/v1/settings`
- media attach and asset retrieval endpoints under `/api/v1/`
- recipe-level AI suggestion endpoints documented in `docs/07_api/implemented-api.md`

Current local tooling:

- Docker-based local deployment
- optional nginx reverse proxy
- file-based local backups and restore
- semantics-first CLI recipe normalization into candidate bundles
- CLI candidate review, patch, ingest, and approval workflows

Not fully shipped yet:

- URL intake in the web UI
- file/image intake in the web UI
- standalone AI tools screens
- full settings UI
- broader route surfaces such as favorites/recent/verified/drafts

## Quick Start

### Docker

Recommended local run path:

```bash
cp .env.example .env
make up
```

Default local addresses:

- Web UI: `http://localhost:3000`
- API health: `http://localhost:8000/api/health`

`make up` creates the required `data/` directories before starting the stack.

### Local Development Without Docker

```bash
# API
cd apps/api
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# Web (separate terminal)
cd apps/web
npm install
npm run dev
```

## Core Commands

### Stack lifecycle

```bash
make up
make up-detach
make up-proxy
make up-proxy-detach
make down
make restart
```

### Logs and shells

```bash
make logs
make logs-api
make logs-web
make logs-nginx
make shell-api
make shell-web
make ps
```

### Build and test

```bash
make build
make rebuild
make test-api

cd apps/web && npm run build
cd apps/api && python -m pytest -v
```

### Backup and restore

```bash
make backup
make backup-db
make backup-list
make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
make backup-prune
```

## Optional LM Studio

LM Studio is optional and runs outside Docker on your host machine. Core archive functionality does not depend on it.

To enable AI-assisted intake normalization:

1. Start LM Studio and load a model.
2. Set these in `.env`:

```env
LM_STUDIO_ENABLED=true
LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
LM_STUDIO_MODEL=<your-model-name>
```

3. Restart the app:

```bash
make restart
```

If LM Studio is unavailable, AI-dependent features fail gracefully and the rest of the archive continues to work.

## Bulk Import Workflow

The web UI covers one-at-a-time intake. For backlog imports, use the CLI workflow.

Raw source files:

- place source files under `data/imports/raw/recipes/`

Generate candidate bundles:

```bash
python3 scripts/import/normalize_recipes.py \
  --file 'data/imports/raw/recipes/Example.md' \
  --file 'data/imports/raw/recipes/Another.md' \
  data/imports/parsed/recipes-candidates \
  --model "Qwen/Qwen2.5-7B-Instruct"
```

Bulk imports now run as a semantics-first staged pipeline. Stage 1 translation/preprocessing returns a `TranslationArtifact` with required `translated_text` and optional `segments`; stage 1.5 matches against the active Swedish reference assets; stage 2 assembles the normalization request with `render_profile`, `locale`, `stage1_translation`, `stage1_reference_match`, and `normalization_policy`. Weak stage-1 quality checks can escalate into `warnings` and `review_flags`, and saved `.preprocessed.txt` artifacts are still supported for one-model-at-a-time LM Studio workflows.

If `--use-preprocessed-dir` does not contain a matching `.preprocessed.txt` artifact for a selected file, the importer currently falls back to inline preprocessing instead of failing the run.

If you can only keep one LM Studio model loaded at a time, run preprocessing and normalization as separate passes:

```bash
python3 scripts/import/normalize_recipes.py \
  --preprocess-only \
  --file 'data/imports/raw/recipes/Example.md' \
  data/imports/preprocessed/recipes \
  --model "translategemma-4b-it"

python3 scripts/import/normalize_recipes.py \
  --use-preprocessed-dir data/imports/preprocessed/recipes \
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

Each preprocessing or normalization run also emits a JSON report under `data/reports/`.
Swedish-source imports also use `data/reference/swedish_recipe_units.json` and `data/reference/swedish_recipe_terms.json` as the active canonical reference inputs for stage-1.5 matching, measurement drift, contextual-term drift, and false-friend risk checks before candidate approval.

Candidate bundles remain backward-compatible with `scripts/import/review_candidates.py`.

## Data Layout

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

## Repository Layout

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

## Documentation Guide

Start here when you need implementation truth:

- `docs/00_overview/current-state.md`
- `docs/01_product/implemented-product.md`
- `docs/02_ux/implemented-routes-and-flows.md`
- `docs/07_api/implemented-api.md`
- `docs/09_ops/local-deployment.md`
- `docs/09_ops/backup-restore.md`
- `docs/10_imports/recipe-import-workflow.md`

Use the broader spec docs under `docs/` when you need target-state design direction, not just current behavior.

## Notes for Contributors

- Keep a clean distinction between implemented behavior and planned behavior.
- Do not document spec-only routes or features as if they are already shipped.
- Preserve the local-first model: data ownership, raw-source evidence, and explicit review boundaries matter.
- For frontend changes, follow the existing dark, archive-first visual system and shared token layer rather than introducing a new visual direction.

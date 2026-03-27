# Repository Guidelines

## Project Structure & Module Organization
`apps/api` contains the FastAPI backend, SQLAlchemy models, intake services, and migrations. `apps/web` is the Vite/React frontend. Shared packages live in `packages/` (`shared-types`, `shared-ui-tokens`, `shared-taxonomy`, `shared-prompts`). Operational docs are in `docs/`, prompt assets in `prompts/`, and local scripts in `scripts/` (`backup`, `import`, `migrate`, `seed`). Runtime data stays under `data/`, especially `data/imports/raw/recipes` and `data/imports/parsed/recipes-candidates`.

## Build, Test, and Development Commands
- `make up` starts the local stack with Docker Compose.
- `make up-proxy` starts the stack behind nginx on the configured proxy port.
- `make test-api` runs backend tests with `pytest`.
- `cd apps/web && npm run dev` runs the frontend locally with Vite.
- `cd apps/web && npm run build` type-checks and builds the frontend.
- `cd apps/api && python -m pytest -v` runs verbose API tests.
- `python3 scripts/import/normalize_recipes.py --file ...` creates one candidate bundle from a raw recipe file.
- `python3 scripts/import/review_candidates.py list|show|edit|ingest|approve` reviews and promotes candidate bundles.

## Coding Style & Naming Conventions
Use 4-space indentation in Python and standard TypeScript formatting in the web app. Prefer explicit, descriptive names: `intake_service.py`, `CandidateUpdate`, `review_candidates.py`. Keep file names lowercase with underscores for Python and kebab/route-oriented names for docs and prompts. Use ASCII unless the source text already requires Swedish names or recipe titles.

## Testing Guidelines
Backend tests use `pytest` and `pytest-asyncio`. Add tests under `apps/api/tests` or the top-level `tests/` tree using `test_*.py` naming. For importer changes, verify both `python3 -m py_compile ...` and one realistic single-file run. Prefer deterministic fixture-based tests for candidate bundle transforms.

## Commit & Pull Request Guidelines
Git history is not available in this workspace snapshot, so use short imperative commit messages with scope, e.g. `api: preserve candidate extras on approval` or `import: add candidate edit command`. PRs should include a concise summary, affected paths, test/verification commands, and screenshots only for frontend changes.

## Security & Configuration Tips
Keep local secrets in `.env`; start from `.env.example`. Treat `data/imports/raw/recipes` as source evidence and avoid editing raw files in place after intake. Do not approve candidate bundles with `review_flags` unless the changes have been manually reviewed.

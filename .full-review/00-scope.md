# Review Scope

## Target

Full codebase review of **Sevastolink Galley Archive** — a local-first, self-hosted recipe archive. Python/FastAPI backend, React/TypeScript frontend, SQLite database, optional LM Studio AI integration.

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy, SQLite + FTS5
- **Frontend:** React 18, TypeScript, Vite, React Router, TanStack Query
- **AI (optional):** LM Studio HTTP client (OpenAI-compatible)
- **Infra:** Docker Compose, Nginx (optional), Systemd (optional)
- **Shared packages:** shared-prompts, shared-taxonomy, shared-ui-tokens, shared-types

## Files

### Backend — apps/api/src/
- ai/: evaluator.py, lm_studio_client.py, metadata_suggester.py, normalizer.py, pantry_suggester.py, rewriter.py, similarity_engine.py
- config/: logging_config.py, settings.py
- db/: database.py, init_db.py
- models/: intake.py, media.py, recipe.py, settings.py
- routes/: health.py, intake.py, media.py, pantry.py, recipes.py, settings.py
- schemas/: ai_outputs.py, common.py, ingredient_families.py, intake.py, media_schema.py, recipe.py, settings_schema.py, taxonomy.py
- services/: intake_service.py, media_service.py, recipe_service.py, settings_service.py
- utils/: ids.py, slugify.py
- main.py

### Backend — apps/api/tests/ (120 tests)
- test_ai_evaluation.py, test_ai_metadata.py, test_ai_pantry.py, test_ai_rewrite.py, test_ai_similarity.py
- test_batch_intake.py, test_error_envelope.py, test_health.py, test_intake.py
- test_media.py, test_prompt_registry.py, test_recipes.py, test_settings.py

### Frontend — apps/web/src/
- components/kitchen/: KitchenHeader.tsx, KitchenIngredients.tsx, KitchenSteps.tsx
- components/library/: FilterPanel.tsx, RecipeRow.tsx, SearchBar.tsx
- components/recipe/: IngredientList.tsx, MetadataStrip.tsx, NoteBlock.tsx, SourcePanel.tsx, StepList.tsx
- components/shell/: AppShell.tsx, SideNav.tsx
- components/ui/: Badge.tsx, Chip.tsx, ConfirmDialog.tsx, Icon.tsx, MetaItem.tsx, StatusBadge.tsx
- hooks/: useBreakpoint.ts, useFavorite.ts, useRecipe.ts, useRecipes.ts, useSettings.ts
- lib/: api.ts, intake-api.ts, media-api.ts, recipe-ai-api.ts, scaling.ts, settings-api.ts
- pages/: IntakePage.tsx, KitchenPage.tsx, LibraryPage.tsx, ManualEntryPage.tsx, PantryPage.tsx, PasteTextPage.tsx, RecipePage.tsx, SettingsPage.tsx
- app/router.tsx, App.tsx, main.tsx, types/recipe.ts

### Shared Packages
- packages/shared-prompts/src/shared_prompts/: contracts.py, loader.py, registry.py
- packages/shared-taxonomy/src/index.ts
- packages/shared-types/src/index.ts
- packages/shared-ui-tokens/src/index.ts

### Infrastructure & Scripts
- docker-compose.yml
- infra/nginx/galley.conf
- infra/systemd/galley.service, galley-proxy.service, install.sh
- scripts/backup/backup.sh, restore.sh, schedule-daily.sh
- scripts/dev/check.sh, reset.sh
- scripts/import/: normalize_recipes.py, repair_candidates.py, review_candidates.py, recipe_import/ (pipeline, transforms, transport, etc.)
- scripts/migrate/run.sh
- scripts/seed/seed_dev.py

## Flags

- Security Focus: no
- Performance Critical: no
- Strict Mode: no
- Framework: FastAPI + React (auto-detected)

## Review Phases

1. Code Quality & Architecture
2. Security & Performance
3. Testing & Documentation
4. Best Practices & Standards
5. Consolidated Report

# Recipe CRUD + Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a complete recipe CRUD API, Library screen, and Recipe Detail screen — the first fully usable archive vertical slice.

**Architecture:** FastAPI service layer (`recipe_service.py`) called from route handlers, no separate repository. SQLite FTS5 for text search, direct ORM filters for facets. Frontend uses TanStack Query + a typed fetch wrapper, URL search params for filter state. Response envelope `{data, meta}` on all routes.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, SQLite FTS5, React 18, TypeScript 5, TanStack Query v5, React Router v6.

---

## File Map

### Backend
- Create: `apps/api/src/utils/__init__.py`
- Create: `apps/api/src/utils/ids.py` — ULID generator (stdlib only)
- Create: `apps/api/src/utils/slugify.py` — slug from title + collision suffix
- Create: `apps/api/src/schemas/common.py` — ApiResponse, ListMeta, ErrorDetail
- Modify: `apps/api/src/schemas/recipe.py` — full Pydantic v2 schema expansion
- Create: `apps/api/src/services/__init__.py`
- Create: `apps/api/src/services/recipe_service.py` — CRUD + search + FTS sync
- Create: `apps/api/src/routes/recipes.py` — all recipe endpoints under `/api/v1`
- Modify: `apps/api/src/main.py` — mount v1 router at `/api/v1`
- Create: `apps/api/tests/test_recipes.py` — endpoint tests

### Frontend
- Create: `apps/web/src/lib/api.ts` — typed fetch wrapper
- Create: `apps/web/src/types/recipe.ts` — TS interfaces
- Create: `apps/web/src/hooks/useRecipes.ts` — TanStack Query list
- Create: `apps/web/src/hooks/useRecipe.ts` — single recipe
- Create: `apps/web/src/components/ui/StatusBadge.tsx`
- Create: `apps/web/src/components/library/RecipeRow.tsx`
- Create: `apps/web/src/components/library/SearchBar.tsx`
- Create: `apps/web/src/components/library/FilterPanel.tsx`
- Create: `apps/web/src/components/recipe/MetadataStrip.tsx`
- Create: `apps/web/src/components/recipe/IngredientList.tsx`
- Create: `apps/web/src/components/recipe/StepList.tsx`
- Create: `apps/web/src/components/recipe/NoteBlock.tsx`
- Create: `apps/web/src/components/recipe/SourcePanel.tsx`
- Modify: `apps/web/src/pages/LibraryPage.tsx`
- Modify: `apps/web/src/pages/RecipePage.tsx`

---

## Task 1: Utility layer — IDs and slugs

**Files:**
- Create: `apps/api/src/utils/__init__.py`
- Create: `apps/api/src/utils/ids.py`
- Create: `apps/api/src/utils/slugify.py`

- [ ] Create `utils/__init__.py` (empty)
- [ ] Write `ids.py` — ULID generator using time + random, Crockford base32
- [ ] Write `slugify.py` — lowercase, replace non-alphanumeric with hyphens, dedupe hyphens
- [ ] Verify: `python -c "from src.utils.ids import new_ulid; from src.utils.slugify import slugify; print(new_ulid()); print(slugify('Chicken Stock & Herb Broth'))"`
- [ ] Expected: 26-char ID + `chicken-stock-herb-broth`

## Task 2: Common response schemas

**Files:**
- Create: `apps/api/src/schemas/common.py`

- [ ] Write `common.py` — `ListMeta`, `ApiResponse[T]`, `ListResponse[T]`, `ErrorDetail`
- [ ] Verify: `python -c "from src.schemas.common import ListMeta, ApiResponse; print('OK')"`

## Task 3: Full recipe schemas

**Files:**
- Modify: `apps/api/src/schemas/recipe.py`

- [ ] Write ingredient/step/note/source input and output schemas
- [ ] Write `RecipeCreate`, `RecipeUpdate`, `RecipeDetail`, `RecipeSummaryOut`, `RecipeArchiveResult`
- [ ] Verify: `python -c "from src.schemas.recipe import RecipeCreate, RecipeDetail, RecipeUpdate; print('OK')"`

## Task 4: Recipe service — write path

**Files:**
- Create: `apps/api/src/services/__init__.py`
- Create: `apps/api/src/services/recipe_service.py`

- [ ] Write `create_recipe(db, data: RecipeCreate) -> Recipe` — generates ULID, slug, saves all sub-rows, syncs FTS
- [ ] Write `_sync_fts(db, recipe) -> None` — upsert row in recipe_search_fts
- [ ] Write `_build_ingredient_text(ingredients) -> str` — flat string of item names
- [ ] Verify: `python -c "from src.services.recipe_service import create_recipe; print('OK')"`

## Task 5: Recipe service — read + search path

**Files:**
- Modify: `apps/api/src/services/recipe_service.py`

- [ ] Write `get_recipe(db, id_or_slug: str) -> Recipe | None` — supports ULID or slug
- [ ] Write `list_recipes(db, params) -> tuple[list[Recipe], int]` — FTS + facet filters, pagination, sort
- [ ] Write `update_recipe(db, id, data: RecipeUpdate) -> Recipe | None` — partial update, array replace for ingredients/steps, FTS sync
- [ ] Write `archive_recipe(db, id) -> Recipe | None` — sets state + flag
- [ ] Write `unarchive_recipe(db, id) -> Recipe | None`
- [ ] Write `delete_recipe(db, id) -> bool`
- [ ] Write `set_favorite(db, id, value: bool) -> Recipe | None`
- [ ] Verify: `python -c "from src.services.recipe_service import get_recipe, list_recipes, update_recipe; print('OK')"`

## Task 6: Write recipe endpoint tests (failing first)

**Files:**
- Create: `apps/api/tests/test_recipes.py`

- [ ] Write test: `test_create_recipe` — POST /api/v1/recipes → 201 with id + slug
- [ ] Write test: `test_get_recipe_by_slug` — GET /api/v1/recipes/{slug} → 200 with full detail
- [ ] Write test: `test_list_recipes_empty` — GET /api/v1/recipes → 200 with empty data array, meta.total=0
- [ ] Write test: `test_list_recipes_search` — create one, GET ?q=title_word → returns it
- [ ] Write test: `test_list_recipes_filter_verification` — filter by verification_state
- [ ] Write test: `test_update_recipe` — PATCH → 200 updated fields
- [ ] Write test: `test_archive_recipe` — POST .../archive → 200 archived=true
- [ ] Write test: `test_delete_recipe` — DELETE → 204
- [ ] Run: `pytest tests/test_recipes.py -v` — Expected: all FAIL (routes not implemented)

## Task 7: Recipe routes

**Files:**
- Create: `apps/api/src/routes/recipes.py`

- [ ] Implement all route handlers calling recipe_service
- [ ] Wire the response envelope for all responses
- [ ] Run: `pytest tests/test_recipes.py -v` — Expected: all PASS

## Task 8: Mount v1 router in main.py

**Files:**
- Modify: `apps/api/src/main.py`

- [ ] Create `v1_router`, include `recipes.router`
- [ ] Mount `v1_router` at `/api/v1`
- [ ] Run: `pytest tests/ -v` — health + recipe tests all PASS

## Task 9: Frontend types + API client

**Files:**
- Create: `apps/web/src/types/recipe.ts`
- Create: `apps/web/src/lib/api.ts`

- [ ] Write TS interfaces: `RecipeSummary`, `RecipeDetail`, `Ingredient`, `Step`, `Note`, `Source`
- [ ] Write `api.ts` with `apiFetch<T>` that handles envelope unwrapping and error throws
- [ ] Write `getRecipes(params)` and `getRecipe(slug)` fetch functions
- [ ] Verify: `npm run type-check` passes

## Task 10: TanStack Query hooks

**Files:**
- Create: `apps/web/src/hooks/useRecipes.ts`
- Create: `apps/web/src/hooks/useRecipe.ts`

- [ ] Write `useRecipes(params: RecipeListParams)` — useQuery wrapping `getRecipes`
- [ ] Write `useRecipe(slug: string)` — useQuery wrapping `getRecipe`, enabled when slug truthy
- [ ] Verify: `npm run type-check` passes

## Task 11: UI components — StatusBadge + RecipeRow

**Files:**
- Create: `apps/web/src/components/ui/StatusBadge.tsx`
- Create: `apps/web/src/components/library/RecipeRow.tsx`

- [ ] Write `StatusBadge` — small badge for verification state (Draft/Unverified/Verified/Archived) with token-mapped color
- [ ] Write `RecipeRow` — dense list row: title, cuisine/role/technique metadata, time, status badge, favorite mark
- [ ] Verify: `npm run build` passes

## Task 12: SearchBar + FilterPanel

**Files:**
- Create: `apps/web/src/components/library/SearchBar.tsx`
- Create: `apps/web/src/components/library/FilterPanel.tsx`

- [ ] Write `SearchBar` — controlled input, debounced update, clear button, accessible label
- [ ] Write `FilterPanel` — filter groups: Verification State, Dish Role, Cuisine, Technique; each as clickable chip list; "clear all" action
- [ ] Verify: `npm run build` passes

## Task 13: Recipe detail components

**Files:**
- Create: `apps/web/src/components/recipe/MetadataStrip.tsx`
- Create: `apps/web/src/components/recipe/IngredientList.tsx`
- Create: `apps/web/src/components/recipe/StepList.tsx`
- Create: `apps/web/src/components/recipe/NoteBlock.tsx`
- Create: `apps/web/src/components/recipe/SourcePanel.tsx`

- [ ] Write `MetadataStrip` — horizontal band: dish role / cuisine / technique / time / servings / complexity / trust state
- [ ] Write `IngredientList` — grouped ingredients (group heading if present), quantity+unit+item+prep
- [ ] Write `StepList` — numbered steps with optional time note
- [ ] Write `NoteBlock` — labeled note sections (recipe/service/storage/substitution)
- [ ] Write `SourcePanel` — source type, title/author/URL, raw source text (collapsed)
- [ ] Verify: `npm run build` passes

## Task 14: Library page — real implementation

**Files:**
- Modify: `apps/web/src/pages/LibraryPage.tsx`

- [ ] Use `useSearchParams` for filter state (q, dish_role, primary_cuisine, technique_family, verification_state, favorite)
- [ ] Wire `useRecipes(params)` for data
- [ ] Render: SearchBar + FilterPanel + recipe list (RecipeRow × results) + loading/empty states
- [ ] Clicking a row navigates to `/recipe/:slug`
- [ ] Verify: `npm run build` passes

## Task 15: Recipe detail page — real implementation

**Files:**
- Modify: `apps/web/src/pages/RecipePage.tsx`

- [ ] Use `useParams({ slug })` to get slug
- [ ] Wire `useRecipe(slug)` for data
- [ ] Render: title + status badge + action row (Kitchen Mode link, favorite) + MetadataStrip + IngredientList + StepList + NoteBlock + SourcePanel
- [ ] Loading and not-found states
- [ ] Verify: `npm run build` passes

---

## Final Verification Commands

```bash
# Backend
cd apps/api && pytest tests/ -v
# Expected: all PASS

# Full build (type-check + bundle)
cd apps/web && npm run build
# Expected: 0 TS errors, bundle output

# Run both services and smoke test
cd apps/api && uvicorn src.main:app --reload --port 8000 &
cd apps/web && npm run dev &
curl http://localhost:8000/api/v1/recipes
# Expected: {"data":[],"meta":{"total":0,"limit":50,"offset":0}}
```

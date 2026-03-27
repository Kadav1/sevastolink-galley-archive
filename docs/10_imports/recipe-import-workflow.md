# Sevastolink Galley Archive

## Recipe Import Workflow v1.0

---

## 1. Purpose

This document defines the current bulk import and candidate review workflow for recipe source files.

It establishes:

* where raw source files should live
* how candidate bundles are generated
* how candidate bundles are reviewed and patched
* how reviewed candidates enter the intake database
* how reviewed candidates are approved into canonical recipes
* how this CLI workflow relates to the current web intake surfaces

This is an implementation-aware workflow document for the current repository.

---

## 2. Workflow philosophy

### Established facts

* Raw source, structured candidate, and approved recipe are distinct states in this product.
* Raw recipe source files are preserved as evidence.
* Candidate bundles are intermediate review artifacts, not approved records.
* Approval into the canonical archive is explicit and review-driven.

### Workflow standard

The bulk import workflow should preserve the archive-first model:

* raw source files remain unchanged
* normalization writes a separate candidate artifact
* review happens on the candidate artifact
* ingest and approval reuse the existing intake service rather than bypassing it

---

## 3. Directory model

### Raw source input

Place raw source files under:

`data/imports/raw/recipes/`

Recommended source formats:

* `.md`
* `.txt`

### Candidate output

Write normalization output to:

`data/imports/parsed/recipes-candidates/`

Each normalized file becomes a `.candidate.json` bundle.

### Archive rule

Do not edit raw source files in place after they have been treated as intake evidence.

---

## 4. Workflow stages

### 4.1 Stage 1: Collect raw source

Add raw recipe files to `data/imports/raw/recipes/`.

These files are the source-of-evidence layer for the import pipeline.

### 4.2 Stage 2: Normalize into candidate bundles

Run:

```bash
python3 scripts/import/normalize_recipes.py \
  data/imports/raw/recipes \
  data/imports/parsed/recipes-candidates \
  --model "Qwen/Qwen2.5-7B-Instruct"
```

Single-file normalization is also supported:

```bash
python3 scripts/import/normalize_recipes.py \
  --file 'data/imports/raw/recipes/Burgarsås.md' \
  data/imports/parsed/recipes-candidates \
  --model "Qwen/Qwen2.5-7B-Instruct"
```

Current expectations:

* LM Studio must be reachable at the chosen base URL
* the runtime prompt and schema files must exist
* output is written as candidate bundle JSON, not directly into the database

### 4.3 Stage 3: Review candidate bundles

List available bundles:

```bash
python3 scripts/import/review_candidates.py list
```

Inspect one bundle:

```bash
python3 scripts/import/review_candidates.py show \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'
```

Review should focus on:

* title quality
* ingredient completeness
* step quality
* preserved provenance
* suspicious AI guesses
* taxonomy values that look too broad, too narrow, or invented

### 4.4 Stage 4: Patch candidate bundles when needed

Apply a patch file:

```bash
python3 scripts/import/review_candidates.py edit \
  'data/imports/parsed/recipes-candidates/Gyllenpenne.candidate.json' \
  --patch /tmp/gyllenpenne-fix.json \
  --clear-review-flags \
  --clear-warnings
```

Current behavior:

* `edit` mutates the bundle file itself
* it does not modify the raw source file
* it does not approve anything by itself

### 4.5 Stage 5: Ingest reviewed candidates into intake

Ingest a reviewed bundle:

```bash
python3 scripts/import/review_candidates.py ingest \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'
```

Purpose:

* create `intake_jobs` and `structured_candidates` records using the existing intake service

This is useful when the candidate should enter the normal intake database for review without yet becoming a canonical recipe.

### 4.6 Stage 6: Approve candidates into recipes

Approve a reviewed bundle:

```bash
python3 scripts/import/review_candidates.py approve \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'
```

Purpose:

* promote the reviewed candidate into `recipes` through the intake approval flow

Current safety rule:

* approval refuses bundles with `review_flags` unless `--allow-review-flags` is supplied

This safety rule exists because candidate bundles with review flags still require explicit human judgment.

---

## 5. Candidate bundle model

### Established facts

Candidate bundles are filesystem artifacts produced by the normalization script.

They are not the same thing as:

* raw source files
* intake database rows
* approved recipes

### Current contents

A candidate bundle includes:

* source metadata
* normalized candidate update fields
* optional candidate extras
* warning list
* review flag list
* prompt and schema provenance

### Patch file shape

Patch files applied by `review_candidates.py edit` should use this structure:

```json
{
  "candidate_update": {
    "title": "Golden Penne",
    "ingredients": [
      {
        "position": 1,
        "quantity": "2",
        "unit": "cloves",
        "item": "garlic",
        "preparation": "finely chopped",
        "optional": false
      }
    ]
  },
  "candidate_extras": {
    "secondary_cuisines": ["Italian"]
  }
}
```

---

## 6. Relationship to the web intake flow

### Current web surfaces

The current web app supports:

* manual entry
* paste-text intake
* optional AI normalization during paste-text intake

### Current distinction

The CLI import flow is the better fit when:

* working from many source files
* preserving source files in bulk
* reviewing normalization output outside the web UI
* patching candidate bundles directly before ingest or approval

The web flow is the better fit when:

* entering one recipe manually
* pasting one raw recipe source at a time
* interactively editing candidate fields in-browser

Both paths preserve the same product boundary:

* raw source
* candidate
* approved recipe

---

## 7. Operational notes

### Review flags

`review_flags` are stronger than ordinary warnings.

They indicate that the candidate should not be approved casually. Typical reasons include:

* likely missing ingredient structure
* questionable taxonomy assignments
* uncertain source interpretation
* AI output that appears overconfident or invented

### Force-new behavior

`ingest` and `approve` both support `--force-new`.

Use this only when a fresh intake job is required even though the bundle has already been ingested once.

### Database dependency

`review_candidates.py` initializes the local database and then works through the backend intake service layer. It is not a disconnected JSON-only utility.

---

## 8. Common command set

```bash
# Normalize a directory of raw recipe files
python3 scripts/import/normalize_recipes.py \
  data/imports/raw/recipes \
  data/imports/parsed/recipes-candidates \
  --model "Qwen/Qwen2.5-7B-Instruct"

# List candidate bundles
python3 scripts/import/review_candidates.py list

# Show one candidate bundle
python3 scripts/import/review_candidates.py show \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'

# Patch a candidate bundle in place
python3 scripts/import/review_candidates.py edit \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json' \
  --patch /tmp/fix.json \
  --clear-review-flags \
  --clear-warnings

# Ingest without approval
python3 scripts/import/review_candidates.py ingest \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'

# Approve into canonical recipes
python3 scripts/import/review_candidates.py approve \
  'data/imports/parsed/recipes-candidates/Burgarsås.candidate.json'
```

---

## 9. Current limitations

The current bulk import workflow does not yet provide:

* a dedicated web review queue for candidate bundles
* URL import
* image or PDF parsing through the current web app
* background job orchestration for batch imports

Those remain valid future directions, but the current supported workflow is the CLI pipeline described here.

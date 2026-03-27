# Prompt Workspace

This directory contains prompt assets used to build, organize, validate, and run Sevastolink Galley Archive prompt workflows.

## Structure

* `build/claude/anchors/` - reusable anchor prompts and context blocks
* `build/claude/sessions/` - staged session prompts for major build phases
* `build/claude/specs/` - specification prompts aligned to canonical project documents
* `build/claude/codegen/` - code-generation and implementation prompts
* `build/claude/archive/pre-foundation/` - archived pre-foundation prompt material
* `runtime/normalization/` - runtime normalization prompts
* `runtime/translation/` - runtime translation prompts
* `runtime/metadata/` - runtime metadata prompts
* `runtime/rewrite/` - runtime rewrite prompts
* `runtime/pantry/` - runtime pantry prompts
* `runtime/similarity/` - runtime similarity prompts
* `runtime/evaluation/` - evaluation prompts and QA cases
* `schemas/` - prompt and output schemas
* `fixtures/` - fixture inputs and expected outputs for testing

## Current status

Populated:

* `build/claude/anchors/`
* `build/claude/sessions/`
* `build/claude/specs/`
* `build/claude/codegen/`
* `build/claude/archive/pre-foundation/`
* `build/claude/archive/post-foundation/`
* `runtime/`
* `schemas/`

Notable coverage now included:

* normalized pre-foundation archive stage prompts
* implementation session prompts through:
  * `session-11-shared-prompts-runtime-wiring.md`
  * `session-12-shared-ui-tokens-and-adoption.md`
* normalized codegen prompts for bootstrap, database, API, frontend shell, intake, AI normalization, Kitchen Mode, and testing/dev ergonomics
* normalized spec prompts for architecture, schema, API, AI, prompt contracts, screen blueprints, frontend mapping, intake pipeline, and v1 build planning
* runtime AI prompt files plus output schemas for structured validation

Reserved but not yet substantially populated:

* `fixtures/`

Empty directories are kept in version control with `.gitkeep` files.

## Implementation note

Prompt assets in `runtime/` are not all wired into the product yet.

Currently implemented prompt usage:

* `normalization/` - used by the API intake normalization flow
* `translation/` - used by the CLI recipe importer

Registered but not yet surfaced as implemented product flows:

* `evaluation/`
* `metadata/`
* `rewrite/`
* `pantry/`
* `similarity/`

## Build prompt coverage

The `build/` tree is a development-time authoring archive, not a runtime dependency.

Current interpretation:

* `build/claude/specs/` largely corresponds to canonical docs that exist under `docs/`
* many `build/claude/sessions/` prompts correspond to code or infra that now exists in the repo
* some `build/claude/codegen/` prompts only partially materialized in implementation

The clearest partially implemented build-prompt areas are:

* search-domain/API work
* AI review/evaluation flow beyond normalization
* higher-level dev, migration, seed, and end-to-end test scaffolding

So `build/` should be read primarily as implementation history and planning provenance, not as proof that the checkout is missing generated code.

# Sevastolink Galley Archive

## Shared Prompts Package v1.0

---

## 1. Purpose

This package defines the runtime prompt registry used by the application.

It establishes:

* how runtime prompt families are registered
* where prompt files and schemas live in the repository
* how application code resolves prompt contracts
* how new runtime prompt families should be added

This package is for runtime prompt wiring. It does not own the build-time prompt authoring archive under `prompts/build/`.

---

## 2. Package role

### Established facts

* Runtime prompt content lives under `prompts/runtime/`.
* Runtime output schemas live under `prompts/schemas/`.
* This package resolves those assets into application-usable prompt contracts.

### Current standard

The package should remain:

* small
* path-aware
* versioned by prompt family
* focused on runtime prompt lookup rather than prompt authoring

---

## 3. Current contents

The package currently provides:

* `contracts.py` — prompt contract model
* `loader.py` — prompt text and schema loading helpers
* `registry.py` — canonical runtime prompt registry

Current registered runtime families:

* `normalization`
* `translation`
* `evaluation`
* `metadata`
* `rewrite`
* `pantry`
* `similarity`

Current implementation note:

* `normalization` is used by the running API normalization flow
* `translation` is used by the CLI importer
* the remaining registered families are prompt assets reserved for future runtime adoption

---

## 4. Repository relationship

This package points into repository-level prompt assets:

* `prompts/runtime/`
* `prompts/schemas/`

It does not copy prompt text into the package itself.

That keeps prompt files:

* inspectable
* editable as plain repository assets
* versioned alongside their schemas and docs

---

## 5. Adding a new runtime prompt family

To add a new runtime prompt family:

1. Add the prompt file under `prompts/runtime/<family>/`.
2. Add the structured output schema under `prompts/schemas/` if required.
3. Register the family and version in `src/shared_prompts/registry.py`.
4. Update the default version map.
5. Add or update tests that validate registry coverage and loadability.

### Current warning

Build-time prompt artifacts under `prompts/build/` are not automatically runtime contracts. Register only prompts that the running application should use.

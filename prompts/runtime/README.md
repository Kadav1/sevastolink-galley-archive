# Runtime Prompts

This folder contains prompts the product can send to LM Studio at runtime.

## Included now

- `normalization/recipe-normalization-v1.md`
- `translation/recipe-translation-v1.md`
- `metadata/metadata-suggestion-v1.md`
- `rewrite/archive-rewrite-v1.md`
- `pantry/pantry-suggestion-v1.md`
- `similarity/similar-recipes-v1.md`
- `evaluation/normalization-review-v1.md`

## Current implementation status

Implemented runtime usage:

- `normalization/recipe-normalization-v1.md`
- `translation/recipe-translation-v1.md`

Prompt assets present but not yet wired to implemented product flows:

- `metadata/metadata-suggestion-v1.md`
- `rewrite/archive-rewrite-v1.md`
- `pantry/pantry-suggestion-v1.md`
- `similarity/similar-recipes-v1.md`
- `evaluation/normalization-review-v1.md`

## Design rules

- Runtime prompts are archive-first, not chat-first
- Outputs should be structured and reviewable
- Prompts must preserve the distinction between raw source, structured candidate, and approved recipe
- AI remains optional and must degrade gracefully when unavailable

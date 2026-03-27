# Raw Recipe Source Files

Place raw recipe source files for bulk normalization here.

Recommended file types:
- `.md`
- `.txt`

This folder is intended for source-first intake material only.
Do not place approved recipe exports here.
Do not edit files in place after they are treated as intake evidence.

Suggested use:
- drop raw source files into this directory
- run `scripts/import/normalize_recipes.py` against this directory
- write output candidate bundles to a separate output directory

Example:

```bash
python3 scripts/import/normalize_recipes.py \
  data/imports/raw/recipes \
  data/imports/parsed/recipes-candidates \
  --model "qwen/qwen3.5-9b"
```

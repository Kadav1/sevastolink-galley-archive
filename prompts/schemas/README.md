# Prompt Output Schemas

These JSON Schema files define the expected structured outputs for the LM Studio runtime prompts used by Sevastolink Galley Archive.

Files included:
- recipe-normalization-output.schema.json
- recipe-translation-output.schema.json
- metadata-suggestion-output.schema.json
- archive-rewrite-output.schema.json
- pantry-suggestion-output.schema.json
- similar-recipes-output.schema.json
- normalization-review-output.schema.json

Use these to validate model output before allowing candidate data into the review flow.

Not every schema in this directory is currently exercised by the running product.
At present, the implemented flows use:

- recipe-normalization-output.schema.json
- recipe-translation-output.schema.json

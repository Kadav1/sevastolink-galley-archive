// Sevastolink Galley Archive — TanStack Query key factory
// Centralises all query keys so invalidations and queries always match.

import type { RecipeListParams } from "../types/recipe";

export const queryKeys = {
  recipes: {
    all: (): readonly ["recipes"] => ["recipes"],
    list: (
      params?: RecipeListParams,
    ): readonly ["recipes", RecipeListParams | undefined] => [
      "recipes",
      params,
    ],
  },
  recipe: {
    detail: (slug: string): readonly ["recipe", string] => ["recipe", slug],
  },
  settings: (): readonly ["settings"] => ["settings"],
} as const;

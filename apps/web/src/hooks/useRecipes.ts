import { useQuery } from "@tanstack/react-query";
import { getRecipes } from "../lib/api";
import { queryKeys } from "../lib/queryKeys";
import type { RecipeListParams } from "../types/recipe";

export function useRecipes(params: RecipeListParams = {}) {
  return useQuery({
    queryKey: queryKeys.recipes.list(params),
    queryFn: () => getRecipes(params),
    placeholderData: (prev) => prev,
  });
}

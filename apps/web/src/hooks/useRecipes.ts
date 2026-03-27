import { useQuery } from "@tanstack/react-query";
import { getRecipes } from "../lib/api";
import type { RecipeListParams } from "../types/recipe";

export function useRecipes(params: RecipeListParams = {}) {
  return useQuery({
    queryKey: ["recipes", params],
    queryFn: () => getRecipes(params),
    placeholderData: (prev) => prev,
  });
}

import { useQuery } from "@tanstack/react-query";
import { getRecipe } from "../lib/api";
import { queryKeys } from "../lib/queryKeys";

export function useRecipe(slug: string) {
  return useQuery({
    queryKey: queryKeys.recipe.detail(slug),
    queryFn: () => getRecipe(slug),
    enabled: Boolean(slug),
  });
}

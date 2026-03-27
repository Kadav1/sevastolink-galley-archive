import { useQuery } from "@tanstack/react-query";
import { getRecipe } from "../lib/api";

export function useRecipe(slug: string) {
  return useQuery({
    queryKey: ["recipe", slug],
    queryFn: () => getRecipe(slug),
    enabled: Boolean(slug),
  });
}

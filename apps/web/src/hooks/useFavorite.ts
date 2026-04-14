import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toggleFavorite } from "../lib/api";
import { queryKeys } from "../lib/queryKeys";

export function useFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slug, isFavorite }: { slug: string; isFavorite: boolean }) =>
      toggleFavorite(slug, isFavorite),
    onSuccess: (_data, { slug }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all() });
      queryClient.invalidateQueries({
        queryKey: queryKeys.recipe.detail(slug),
      });
    },
  });
}

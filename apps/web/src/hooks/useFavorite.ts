import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toggleFavorite } from "../lib/api";

export function useFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slug, isFavorite }: { slug: string; isFavorite: boolean }) =>
      toggleFavorite(slug, isFavorite),
    onSuccess: (_data, { slug }) => {
      queryClient.invalidateQueries({ queryKey: ["recipes"] });
      queryClient.invalidateQueries({ queryKey: ["recipe", slug] });
    },
  });
}

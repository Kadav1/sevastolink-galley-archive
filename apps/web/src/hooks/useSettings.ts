import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getSettings, updateSettings } from "../lib/settings-api";
import type { SettingsUpdate } from "../lib/settings-api";

export function useSettings() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: () => getSettings().then((r) => r.data),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: SettingsUpdate) =>
      updateSettings(update).then((r) => r.data),
    onSuccess: (data) => {
      queryClient.setQueryData(["settings"], data);
    },
  });
}

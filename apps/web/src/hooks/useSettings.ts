import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getSettings, updateSettings } from "../lib/settings-api";
import type { SettingsUpdate } from "../lib/settings-api";
import { queryKeys } from "../lib/queryKeys";

export function useSettings() {
  return useQuery({
    queryKey: queryKeys.settings(),
    queryFn: () => getSettings().then((r) => r.data),
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: SettingsUpdate) =>
      updateSettings(update).then((r) => r.data),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.settings(), data);
    },
  });
}

import { apiFetch } from "./api";
import type { ApiResponse } from "./api";

export interface Settings {
  default_verification_state: "Draft" | "Unverified";
  library_default_sort:
    | "updated_at_desc"
    | "created_at_desc"
    | "title_asc"
    | "title_desc";
  ai_enabled: boolean;
}

export interface SettingsUpdate {
  default_verification_state?: Settings["default_verification_state"];
  library_default_sort?: Settings["library_default_sort"];
}

export async function getSettings(): Promise<ApiResponse<Settings>> {
  return apiFetch<ApiResponse<Settings>>("/settings");
}

export async function updateSettings(
  update: SettingsUpdate
): Promise<ApiResponse<Settings>> {
  return apiFetch<ApiResponse<Settings>>("/settings", {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}

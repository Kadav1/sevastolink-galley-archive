import type { ListMeta, RecipeDetail, RecipeListParams, RecipeSummary } from "../types/recipe";

const BASE = "/api/v1";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
}

export interface ListResponse<T> {
  data: T[];
  meta: ListMeta;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ── Core fetch ────────────────────────────────────────────────────────────────

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    let code = "internal_error";
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      code = body?.error?.code ?? code;
      message = body?.error?.message ?? message;
    } catch {
      // ignore parse failure
    }
    throw new ApiError(res.status, code, message);
  }

  return res.json() as Promise<T>;
}

// ── Recipe endpoints ──────────────────────────────────────────────────────────

export async function getRecipes(
  params: RecipeListParams = {}
): Promise<ListResponse<RecipeSummary>> {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      qs.set(key, String(value));
    }
  }
  const query = qs.toString() ? `?${qs.toString()}` : "";
  return apiFetch<ListResponse<RecipeSummary>>(`/recipes${query}`);
}

export async function getRecipe(
  slug: string
): Promise<ApiResponse<RecipeDetail>> {
  return apiFetch<ApiResponse<RecipeDetail>>(`/recipes/${slug}`);
}

export async function toggleFavorite(
  slug: string,
  isFavorite: boolean
): Promise<ApiResponse<RecipeSummary>> {
  const action = isFavorite ? "unfavorite" : "favorite";
  return apiFetch<ApiResponse<RecipeSummary>>(`/recipes/${slug}/${action}`, {
    method: "POST",
  });
}

export async function patchRecipe(
  idOrSlug: string,
  patch: Record<string, unknown>,
): Promise<ApiResponse<RecipeDetail>> {
  return apiFetch<ApiResponse<RecipeDetail>>(`/recipes/${idOrSlug}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export async function archiveRecipe(
  idOrSlug: string,
): Promise<ApiResponse<{ archived: boolean }>> {
  return apiFetch<ApiResponse<{ archived: boolean }>>(`/recipes/${idOrSlug}/archive`, {
    method: "POST",
  });
}

export async function unarchiveRecipe(
  idOrSlug: string,
): Promise<ApiResponse<{ archived: boolean }>> {
  return apiFetch<ApiResponse<{ archived: boolean }>>(`/recipes/${idOrSlug}/unarchive`, {
    method: "POST",
  });
}

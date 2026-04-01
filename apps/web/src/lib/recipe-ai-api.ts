import { apiFetch } from "./api";

// ── Metadata suggestion ───────────────────────────────────────────────────────

export interface MetadataSuggestionOut {
  dish_role: string | null;
  primary_cuisine: string | null;
  secondary_cuisines: string[];
  technique_family: string | null;
  ingredient_families: string[];
  complexity: string | null;
  time_class: string | null;
  service_format: string | null;
  season: string | null;
  mood_tags: string[];
  storage_profile: string[];
  dietary_flags: string[];
  sector: string | null;
  class: string | null;       // backend alias for operational_class
  heat_window: string | null;
  provision_tags: string[];
  short_description: string | null;
  confidence_notes: string[];
  uncertainty_notes: string[];
}

export async function suggestMetadata(
  idOrSlug: string,
): Promise<{ data: MetadataSuggestionOut }> {
  return apiFetch(`/recipes/${idOrSlug}/suggest-metadata`, { method: "POST" });
}

// ── Archive rewrite ───────────────────────────────────────────────────────────

export interface RewriteIngredientOut {
  amount: string | null;
  unit: string | null;
  item: string;
  note: string | null;
  optional: boolean | null;
  group: string | null;
}

export interface RewriteStepOut {
  step_number: number;
  instruction: string;
  time_note: string | null;
  heat_note: string | null;
  equipment_note: string | null;
}

export interface ArchiveRewriteOut {
  title: string | null;
  short_description: string | null;
  ingredients: RewriteIngredientOut[];
  steps: RewriteStepOut[];
  recipe_notes: string | null;
  service_notes: string | null;
  rewrite_notes: string[];
  uncertainty_notes: string[];
}

export async function rewriteRecipe(
  idOrSlug: string,
): Promise<{ data: ArchiveRewriteOut }> {
  return apiFetch(`/recipes/${idOrSlug}/rewrite`, { method: "POST" });
}

// ── Similar recipes ───────────────────────────────────────────────────────────

export interface SimilarityMatchOut {
  title: string;
  similarity_score_band: string;
  primary_similarity_reason: string;
  secondary_similarity_reasons: string[];
  major_differences: string[];
}

export interface SimilarRecipesOut {
  top_matches: SimilarityMatchOut[];
  near_matches: SimilarityMatchOut[];
  why_each_match_ranked: string[];
  major_difference_notes: string[];
  confidence_notes: string[];
}

export async function findSimilarRecipes(
  idOrSlug: string,
  emphasis?: string,
): Promise<{ data: SimilarRecipesOut }> {
  return apiFetch(`/recipes/${idOrSlug}/similar`, {
    method: "POST",
    body: JSON.stringify({ emphasis: emphasis ?? null }),
  });
}

// ── Pantry suggestion ─────────────────────────────────────────────────────────

export interface PantryMatchOut {
  title: string;
  match_type: string;
  why_it_matches: string;
  missing_items: string[];
  recommended_adjustments: string[];
  time_fit: string | null;
}

export interface PantrySuggestionOut {
  direct_matches: PantryMatchOut[];
  near_matches: PantryMatchOut[];
  pantry_gap_notes: string[];
  substitution_suggestions: string[];
  quick_ideas: string[];
  confidence_notes: string[];
}

export async function suggestPantry(
  availableIngredients: string[],
): Promise<{ data: PantrySuggestionOut }> {
  return apiFetch("/pantry/suggest", {
    method: "POST",
    body: JSON.stringify({ available_ingredients: availableIngredients }),
  });
}

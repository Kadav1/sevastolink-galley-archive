// Sevastolink Galley Archive — Recipe types
// Mirror of apps/api/src/schemas/recipe.py

export type VerificationState =
  | "Draft"
  | "Unverified"
  | "Verified"
  | "Archived";

export type NoteType =
  | "recipe"
  | "service"
  | "storage"
  | "substitution"
  | "source";

export interface Ingredient {
  id: string;
  position: number;
  group_heading: string | null;
  quantity: string | null;
  unit: string | null;
  item: string;
  preparation: string | null;
  optional: boolean;
  display_text: string | null;
}

export interface Step {
  id: string;
  position: number;
  instruction: string;
  time_note: string | null;
  equipment_note: string | null;
}

export interface Note {
  id: string;
  note_type: NoteType;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  source_type: string;
  source_title: string | null;
  source_author: string | null;
  source_url: string | null;
  source_notes: string | null;
  raw_source_text: string | null;
  created_at: string;
}

export interface RecipeSummary {
  id: string;
  slug: string;
  title: string;
  short_description: string | null;
  dish_role: string | null;
  primary_cuisine: string | null;
  technique_family: string | null;
  complexity: string | null;
  time_class: string | null;
  sector: string | null;
  operational_class: string | null;
  servings: string | null;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  total_time_minutes: number | null;
  verification_state: VerificationState;
  favorite: boolean;
  rating: number | null;
  created_at: string;
  updated_at: string;
  last_cooked_at: string | null;
}

export interface RecipeDetail extends RecipeSummary {
  secondary_cuisines: string[];
  service_format: string | null;
  season: string | null;
  ingredient_families: string[];
  mood_tags: string[];
  storage_profile: string[];
  dietary_flags: string[];
  provision_tags: string[];
  heat_window: string | null;
  servings: string | null;
  rest_time_minutes: number | null;
  archived: boolean;
  ingredients: Ingredient[];
  steps: Step[];
  notes: Note[];
  source: Source | null;
  intake_job_id: string | null;
  last_viewed_at: string | null;
}

// API parameter types
export interface RecipeListParams {
  q?: string;
  verification_state?: VerificationState;
  favorite?: boolean;
  archived?: boolean;
  dish_role?: string;
  primary_cuisine?: string;
  technique_family?: string;
  complexity?: string;
  time_class?: string;
  sector?: string;
  operational_class?: string;
  heat_window?: string;
  ingredient_family?: string;
  sort?: string;
  limit?: number;
  offset?: number;
}

export interface ListMeta {
  total: number;
  limit: number;
  offset: number;
}

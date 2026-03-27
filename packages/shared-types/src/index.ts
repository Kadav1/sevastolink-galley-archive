// Sevastolink Galley Archive — shared TypeScript types
// These mirror the backend Pydantic schemas. Keep in sync with apps/api/src/schemas/.

export type VerificationState = "Draft" | "Unverified" | "Verified" | "Archived";

export type IntakeStatus =
  | "captured"
  | "extracting"
  | "structured"
  | "in_review"
  | "approved"
  | "failed"
  | "abandoned";

export type IntakeType = "manual" | "paste_text" | "url" | "file";

export interface RecipeSummary {
  id: string;
  slug: string;
  title: string;
  short_description?: string | null;
  dish_role?: string | null;
  primary_cuisine?: string | null;
  technique_family?: string | null;
  complexity?: string | null;
  time_class?: string | null;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  total_time_minutes?: number | null;
  verification_state: VerificationState;
  favorite: boolean;
  rating?: number | null;
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

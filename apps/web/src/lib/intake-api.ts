import type { VerificationState } from "../types/recipe";
import { apiFetch } from "./api";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface IntakeJobOut {
  id: string;
  intake_type: string;
  status: string;
  parse_status: string;
  ai_status: string;
  review_status: string;
  raw_source_text: string | null;
  source_url: string | null;
  resulting_recipe_id: string | null;
  candidate_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CandidateIngredientIn {
  position: number;
  item: string;
  quantity?: string | null;
  unit?: string | null;
  preparation?: string | null;
  group_heading?: string | null;
  optional?: boolean;
  display_text?: string | null;
}

export interface CandidateStepIn {
  position: number;
  instruction: string;
  time_note?: string | null;
  equipment_note?: string | null;
}

export interface CandidateUpdate {
  title?: string;
  short_description?: string;
  dish_role?: string;
  primary_cuisine?: string;
  technique_family?: string;
  complexity?: string;
  time_class?: string;
  servings?: string;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  notes?: string;
  source_credit?: string;
  ingredients?: CandidateIngredientIn[];
  steps?: CandidateStepIn[];
}

export interface CandidateIngredientOut {
  position: number;
  group_heading: string | null;
  quantity: string | null;
  unit: string | null;
  item: string | null;
  preparation: string | null;
  optional: boolean;
}

export interface CandidateStepOut {
  position: number;
  instruction: string | null;
  time_note: string | null;
  equipment_note: string | null;
}

export interface CandidateOut {
  id: string;
  intake_job_id: string;
  candidate_status: string;
  title: string | null;
  short_description: string | null;
  dish_role: string | null;
  primary_cuisine: string | null;
  technique_family: string | null;
  complexity: string | null;
  time_class: string | null;
  servings: string | null;
  prep_time_minutes: number | null;
  cook_time_minutes: number | null;
  notes: string | null;
  service_notes: string | null;
  source_credit: string | null;
  ingredients: CandidateIngredientOut[];
  steps: CandidateStepOut[];
  created_at: string;
  updated_at: string;
}

export interface ApproveIntakeIn {
  verification_state: VerificationState;
  source_type: string;
  source_title?: string | null;
  source_author?: string | null;
  source_notes?: string | null;
}

export interface ApproveIntakeOut {
  recipe: { id: string; slug: string; title: string; verification_state: VerificationState };
  intake_job_id: string;
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function createIntakeJob(
  intake_type: "manual" | "paste_text",
  raw_source_text?: string,
  source_notes?: string,
): Promise<{ data: IntakeJobOut }> {
  return apiFetch("/intake-jobs", {
    method: "POST",
    body: JSON.stringify({ intake_type, raw_source_text, source_notes }),
  });
}

export async function getIntakeJob(jobId: string): Promise<{ data: IntakeJobOut }> {
  return apiFetch(`/intake-jobs/${jobId}`);
}

export async function updateCandidate(
  jobId: string,
  data: CandidateUpdate,
): Promise<{ data: CandidateOut }> {
  return apiFetch(`/intake-jobs/${jobId}/candidate`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function normalizeCandidate(
  jobId: string,
): Promise<{ data: CandidateOut }> {
  return apiFetch(`/intake-jobs/${jobId}/normalize`, {
    method: "POST",
  });
}

export async function approveIntakeJob(
  jobId: string,
  data: ApproveIntakeIn,
): Promise<{ data: ApproveIntakeOut }> {
  return apiFetch(`/intake-jobs/${jobId}/approve`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

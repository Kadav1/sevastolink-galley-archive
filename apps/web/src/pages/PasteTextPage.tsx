import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../lib/api";
import {
  approveIntakeJob,
  createIntakeJob,
  evaluateCandidate,
  normalizeCandidate,
  updateCandidate,
} from "../lib/intake-api";
import type { CandidateOut, EvaluationOut } from "../lib/intake-api";
import { attachIntakeMedia } from "../lib/media-api";
import type { VerificationState } from "../types/recipe";

// ── Shared input style ────────────────────────────────────────────────────────

const inputStyle: React.CSSProperties = {
  background: "var(--bg-field)",
  border: "1px solid var(--border-subtle)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-primary)",
  fontSize: "var(--text-sm)",
  padding: "var(--space-2) var(--space-3)",
  width: "100%",
};

const labelStyle: React.CSSProperties = {
  fontSize: "var(--text-xs)",
  color: "var(--text-secondary)",
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "var(--tracking-wide)",
};

function Field({
  label,
  required,
  children,
  error,
  aiSuggested,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  error?: string;
  aiSuggested?: boolean;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
      <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
        {label}
        {required && <span style={{ color: "var(--state-advisory)" }}> *</span>}
        {aiSuggested && (
          <span style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", fontWeight: 400, textTransform: "none" as const, letterSpacing: 0 }}>
            ai
          </span>
        )}
      </label>
      {children}
      {error && <p style={{ fontSize: "var(--text-xs)", color: "var(--state-advisory)" }}>{error}</p>}
    </div>
  );
}

// ── Options ───────────────────────────────────────────────────────────────────

const DISH_ROLE_OPTIONS = [
  "", "Breakfast", "Lunch", "Dinner", "Side", "Starter", "Dessert",
  "Snack", "Pantry Staple", "Sauce / Condiment", "Bread", "Drink",
];

const CUISINE_OPTIONS = [
  "", "British", "French", "Italian", "Spanish", "Greek", "Turkish",
  "Levantine", "North African", "West African", "South Asian",
  "East Asian", "South-East Asian", "Japanese", "Chinese", "Korean",
  "Mexican", "American", "Middle Eastern", "Global / Mixed",
];

const TECHNIQUE_OPTIONS = [
  "", "Roast", "Braise", "Simmer", "Fry", "Grill", "Bake",
  "Steam", "Cure / Preserve", "Raw / No-Cook", "Ferment",
];

const VERIFICATION_OPTIONS: { value: VerificationState; label: string }[] = [
  { value: "Draft", label: "Draft — still being shaped" },
  { value: "Unverified", label: "Unverified — stored but not yet trusted" },
  { value: "Verified", label: "Verified — cooked and trusted" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function candidateIngredientsToText(candidate: CandidateOut): string {
  return candidate.ingredients
    .map((ing) => {
      const parts = [ing.quantity, ing.unit, ing.item, ing.preparation].filter(Boolean);
      return parts.join(" ");
    })
    .join("\n");
}

function candidateStepsToText(candidate: CandidateOut): string {
  return candidate.steps
    .map((s, i) => `${i + 1}. ${s.instruction ?? ""}`)
    .join("\n");
}

function parseIngredients(text: string) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, i) => ({ position: i + 1, item: line }));
}

function parseSteps(text: string) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, i) => ({
      position: i + 1,
      instruction: line.replace(/^\d+[.)]\s*/, ""),
    }));
}

// ── Evaluation panel ──────────────────────────────────────────────────────────

const RECOMMENDATION_META: Record<
  EvaluationOut["review_recommendation"],
  { label: string; color: string; bg: string }
> = {
  safe_for_human_review: {
    label: "Safe for review",
    color: "var(--state-verified)",
    bg: "var(--state-verified-bg)",
  },
  review_with_caution: {
    label: "Review with caution",
    color: "var(--state-advisory)",
    bg: "var(--state-advisory-bg)",
  },
  needs_major_correction: {
    label: "Needs major correction",
    color: "var(--state-error)",
    bg: "var(--state-error-bg)",
  },
};

function IssueList({ heading, items }: { heading: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
      <span style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase" as const, letterSpacing: "var(--tracking-wide)" }}>
        {heading}
      </span>
      <ul style={{ margin: 0, paddingLeft: "var(--space-4)", display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
        {items.map((item, i) => (
          <li key={i} style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)", lineHeight: "var(--leading-relaxed)" }}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function EvaluationPanel({
  evaluation,
  onDismiss,
}: {
  evaluation: EvaluationOut;
  onDismiss: () => void;
}) {
  const meta = RECOMMENDATION_META[evaluation.review_recommendation] ?? RECOMMENDATION_META.review_with_caution;
  return (
    <div style={{
      border: `1px solid ${meta.color}`,
      borderRadius: "var(--radius-sm)",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        background: meta.bg,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "var(--space-2) var(--space-3)",
      }}>
        <span style={{ fontSize: "var(--text-xs)", fontWeight: 600, color: meta.color, letterSpacing: "var(--tracking-wide)", textTransform: "uppercase" as const }}>
          {meta.label}
        </span>
        <button
          type="button"
          onClick={onDismiss}
          style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-tertiary)", fontSize: "var(--text-sm)", lineHeight: 1, padding: 0 }}
          aria-label="Dismiss evaluation"
        >
          ×
        </button>
      </div>

      {/* Body */}
      <div style={{ padding: "var(--space-3)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
        <p style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)", lineHeight: "var(--leading-relaxed)", margin: 0 }}>
          {evaluation.fidelity_assessment}
        </p>

        <IssueList heading="Missing information" items={evaluation.missing_information} />
        <IssueList heading="Possible inventions" items={evaluation.likely_inventions_or_overreaches} />
        <IssueList heading="Ingredient issues" items={evaluation.ingredient_issues} />
        <IssueList heading="Step issues" items={evaluation.step_issues} />
        <IssueList heading="Reviewer notes" items={evaluation.reviewer_notes} />

        {evaluation.metadata_confidence && (
          <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", margin: 0 }}>
            Metadata confidence: {evaluation.metadata_confidence}
          </p>
        )}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function PasteTextPage() {
  const navigate = useNavigate();

  // Raw source
  const [rawText, setRawText] = useState("");
  const [sourceNotes, setSourceNotes] = useState("");

  // Intake job created after first AI call or at save time
  const [jobId, setJobId] = useState<string | null>(null);

  // Optional source file — attached to the job after creation
  const [sourceFile, setSourceFile] = useState<File | null>(null);
  const [sourceFileAttached, setSourceFileAttached] = useState(false);

  // Structured fields (editable; may be pre-filled by AI)
  const [title, setTitle] = useState("");
  const [shortDesc, setShortDesc] = useState("");
  const [dishRole, setDishRole] = useState("");
  const [primaryCuisine, setPrimaryCuisine] = useState("");
  const [technique, setTechnique] = useState("");
  const [servings, setServings] = useState("");
  const [prepTime, setPrepTime] = useState("");
  const [cookTime, setCookTime] = useState("");
  const [ingredientsText, setIngredientsText] = useState("");
  const [stepsText, setStepsText] = useState("");
  const [recipeNotes, setRecipeNotes] = useState("");

  // Track which fields were AI-suggested (cleared on user edit)
  const [aiFields, setAiFields] = useState<Set<string>>(new Set());

  // Trust state
  const [verificationState, setVerificationState] = useState<VerificationState>("Unverified");

  // UI state
  const [normalizing, setNormalizing] = useState(false);
  const [normalizeError, setNormalizeError] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);
  const [evaluateError, setEvaluateError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationOut | null>(null);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  // ── Source file attach ─────────────────────────────────────────────────────

  async function attachFileIfPresent(currentJobId: string) {
    if (!sourceFile || sourceFileAttached) return;
    try {
      await attachIntakeMedia(currentJobId, sourceFile);
      setSourceFileAttached(true);
    } catch {
      // Non-fatal — attachment failure doesn't block the intake workflow
    }
  }

  // ── AI normalize ───────────────────────────────────────────────────────────

  async function handleNormalize() {
    if (!rawText.trim()) {
      setErrors({ rawText: "Paste some source text first." });
      return;
    }
    setNormalizing(true);
    setNormalizeError(null);
    setEvaluation(null); // clear any stale evaluation from before re-normalize

    try {
      // Create the intake job if we haven't yet
      let currentJobId = jobId;
      if (!currentJobId) {
        const jobRes = await createIntakeJob("paste_text", rawText.trim(), sourceNotes.trim() || undefined);
        currentJobId = jobRes.data.id;
        setJobId(currentJobId);
      }
      await attachFileIfPresent(currentJobId);

      const res = await normalizeCandidate(currentJobId);
      applyCandidate(res.data);
    } catch (err: unknown) {
      // Surface AI-specific errors as degraded-mode notice rather than hard failure
      if (err instanceof ApiError && (err.code === "ai_disabled" || err.code === "ai_unavailable")) {
        setNormalizeError("AI normalization is unavailable. Fill in the fields manually.");
      } else {
        setNormalizeError(err instanceof Error ? err.message : "Normalization failed.");
      }
    } finally {
      setNormalizing(false);
    }
  }

  async function handleEvaluate() {
    if (!jobId) return;
    setEvaluating(true);
    setEvaluateError(null);
    setEvaluation(null);
    try {
      const res = await evaluateCandidate(jobId);
      setEvaluation(res.data);
    } catch (err: unknown) {
      if (err instanceof ApiError && (err.code === "ai_disabled" || err.code === "ai_unavailable")) {
        setEvaluateError("AI evaluation is unavailable. Continue reviewing manually.");
      } else {
        setEvaluateError(err instanceof Error ? err.message : "Evaluation failed.");
      }
    } finally {
      setEvaluating(false);
    }
  }

  function applyCandidate(c: CandidateOut) {
    const suggested = new Set<string>();

    if (c.title) { setTitle(c.title); suggested.add("title"); }
    if (c.short_description) { setShortDesc(c.short_description); suggested.add("shortDesc"); }
    if (c.dish_role) { setDishRole(c.dish_role); suggested.add("dishRole"); }
    if (c.primary_cuisine) { setPrimaryCuisine(c.primary_cuisine); suggested.add("primaryCuisine"); }
    if (c.technique_family) { setTechnique(c.technique_family); suggested.add("technique"); }
    if (c.servings) { setServings(c.servings); suggested.add("servings"); }
    if (c.prep_time_minutes != null) { setPrepTime(String(c.prep_time_minutes)); suggested.add("prepTime"); }
    if (c.cook_time_minutes != null) { setCookTime(String(c.cook_time_minutes)); suggested.add("cookTime"); }
    if (c.notes) { setRecipeNotes(c.notes); suggested.add("recipeNotes"); }

    if (c.ingredients.length > 0) {
      setIngredientsText(candidateIngredientsToText(c));
      suggested.add("ingredients");
    }
    if (c.steps.length > 0) {
      setStepsText(candidateStepsToText(c));
      suggested.add("steps");
    }

    setAiFields(suggested);
  }

  function clearAiField(field: string) {
    setAiFields((prev) => {
      const next = new Set(prev);
      next.delete(field);
      return next;
    });
  }

  // ── Validation ─────────────────────────────────────────────────────────────

  function validate(): boolean {
    const e: Record<string, string> = {};
    if (!rawText.trim()) e.rawText = "Raw source text is required.";
    if (!title.trim()) e.title = "Title is required.";
    if (verificationState !== "Draft") {
      if (!ingredientsText.trim()) e.ingredients = "At least one ingredient line is required.";
      if (!stepsText.trim()) e.steps = "At least one step is required.";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  // ── Save ───────────────────────────────────────────────────────────────────

  async function handleSave() {
    if (!validate()) return;
    setSaving(true);
    setSaveError(null);

    try {
      // Create the job if it doesn't exist yet (normalize was skipped)
      let currentJobId = jobId;
      if (!currentJobId) {
        const jobRes = await createIntakeJob("paste_text", rawText.trim(), sourceNotes.trim() || undefined);
        currentJobId = jobRes.data.id;
        setJobId(currentJobId);
      }
      await attachFileIfPresent(currentJobId);

      await updateCandidate(currentJobId, {
        title: title.trim(),
        short_description: shortDesc.trim() || undefined,
        dish_role: dishRole || undefined,
        primary_cuisine: primaryCuisine || undefined,
        technique_family: technique || undefined,
        servings: servings.trim() || undefined,
        prep_time_minutes: prepTime ? parseInt(prepTime, 10) : undefined,
        cook_time_minutes: cookTime ? parseInt(cookTime, 10) : undefined,
        notes: recipeNotes.trim() || undefined,
        ingredients: ingredientsText.trim() ? parseIngredients(ingredientsText) : undefined,
        steps: stepsText.trim() ? parseSteps(stepsText) : undefined,
      });

      const approveRes = await approveIntakeJob(currentJobId, {
        verification_state: verificationState,
        source_type: "Manual",
        source_notes: sourceNotes.trim() || undefined,
      });

      navigate(`/recipe/${approveRes.data.recipe.slug}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Save failed.";
      setSaveError(msg);
      setSaving(false);
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  const ai = aiFields;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <Link to="/intake" style={styles.back}>← Intake</Link>
        <h1 style={styles.title}>Paste Text</h1>
        <p style={styles.subtitle}>
          Paste raw recipe text on the left. Fill in the structured fields on the right,
          or use AI to pre-fill them from the source.
          The original text is preserved automatically.
        </p>
      </header>

      <div style={styles.body}>
        {/* Left: raw source */}
        <div style={styles.rawPanel}>
          <div style={styles.panelLabel}>
            <span style={styles.panelLabelText}>Raw source</span>
            <span style={styles.preserved}>preserved on save</span>
          </div>
          {errors.rawText && (
            <p style={{ fontSize: "var(--text-xs)", color: "var(--state-advisory)" }}>
              {errors.rawText}
            </p>
          )}
          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the original recipe text here…"
            style={styles.rawTextarea}
            spellCheck={false}
          />
          <Field label="Source notes">
            <textarea
              value={sourceNotes}
              onChange={(e) => setSourceNotes(e.target.value)}
              rows={2}
              placeholder="Where this came from (optional)"
              style={{ ...inputStyle, resize: "vertical" as const }}
            />
          </Field>

          {/* Optional source image / PDF */}
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
            <span style={labelStyle}>Source image or PDF (optional)</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => {
                setSourceFile(e.target.files?.[0] ?? null);
                setSourceFileAttached(false);
              }}
              style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)" }}
            />
            {sourceFileAttached && (
              <p style={{ fontSize: "var(--text-xs)", color: "var(--state-verified)" }}>
                Source file attached.
              </p>
            )}
          </div>

          {/* Normalize button */}
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            <button
              type="button"
              onClick={handleNormalize}
              disabled={normalizing || !rawText.trim()}
              style={styles.normalizeBtn}
            >
              {normalizing ? "Normalizing…" : "Normalize with AI"}
            </button>
            {normalizeError && (
              <p style={{ fontSize: "var(--text-xs)", color: "var(--state-advisory)" }}>
                {normalizeError}
              </p>
            )}
            {!normalizeError && aiFields.size > 0 && (
              <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
                AI pre-filled {aiFields.size} field{aiFields.size !== 1 ? "s" : ""}. Review and edit before saving.
              </p>
            )}
          </div>

          {/* Evaluate button — only shown after a job exists (normalize was run or job was saved) */}
          {jobId && (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
              <button
                type="button"
                onClick={handleEvaluate}
                disabled={evaluating || normalizing}
                style={styles.evaluateBtn}
              >
                {evaluating ? "Evaluating…" : "Evaluate normalization"}
              </button>
              {evaluateError && (
                <p style={{ fontSize: "var(--text-xs)", color: "var(--state-advisory)" }}>
                  {evaluateError}
                </p>
              )}
            </div>
          )}

          {/* Evaluation result panel */}
          {evaluation && (
            <EvaluationPanel
              evaluation={evaluation}
              onDismiss={() => setEvaluation(null)}
            />
          )}
        </div>

        {/* Right: structured form */}
        <div style={styles.structuredPanel}>
          <div style={styles.panelLabel}>
            <span style={styles.panelLabelText}>Structured record</span>
          </div>

          <div style={styles.formBody}>
            <Field label="Title" required error={errors.title} aiSuggested={ai.has("title")}>
              <input
                value={title}
                onChange={(e) => { setTitle(e.target.value); clearAiField("title"); }}
                placeholder="Recipe title"
                style={inputStyle}
              />
            </Field>

            <Field label="Short description" aiSuggested={ai.has("shortDesc")}>
              <input
                value={shortDesc}
                onChange={(e) => { setShortDesc(e.target.value); clearAiField("shortDesc"); }}
                placeholder="One sentence (optional)"
                style={inputStyle}
              />
            </Field>

            <div style={styles.grid2}>
              <Field label="Dish role" aiSuggested={ai.has("dishRole")}>
                <select
                  value={dishRole}
                  onChange={(e) => { setDishRole(e.target.value); clearAiField("dishRole"); }}
                  style={inputStyle}
                >
                  {DISH_ROLE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
                </select>
              </Field>
              <Field label="Cuisine" aiSuggested={ai.has("primaryCuisine")}>
                <select
                  value={primaryCuisine}
                  onChange={(e) => { setPrimaryCuisine(e.target.value); clearAiField("primaryCuisine"); }}
                  style={inputStyle}
                >
                  {CUISINE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
                </select>
              </Field>
              <Field label="Technique" aiSuggested={ai.has("technique")}>
                <select
                  value={technique}
                  onChange={(e) => { setTechnique(e.target.value); clearAiField("technique"); }}
                  style={inputStyle}
                >
                  {TECHNIQUE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
                </select>
              </Field>
              <Field label="Servings" aiSuggested={ai.has("servings")}>
                <input
                  value={servings}
                  onChange={(e) => { setServings(e.target.value); clearAiField("servings"); }}
                  placeholder="e.g. 4"
                  style={inputStyle}
                />
              </Field>
              <Field label="Prep (min)" aiSuggested={ai.has("prepTime")}>
                <input
                  type="number"
                  value={prepTime}
                  onChange={(e) => { setPrepTime(e.target.value); clearAiField("prepTime"); }}
                  placeholder="20"
                  style={inputStyle}
                />
              </Field>
              <Field label="Cook (min)" aiSuggested={ai.has("cookTime")}>
                <input
                  type="number"
                  value={cookTime}
                  onChange={(e) => { setCookTime(e.target.value); clearAiField("cookTime"); }}
                  placeholder="45"
                  style={inputStyle}
                />
              </Field>
            </div>

            <Field label="Ingredients — one per line" error={errors.ingredients} aiSuggested={ai.has("ingredients")}>
              <textarea
                value={ingredientsText}
                onChange={(e) => { setIngredientsText(e.target.value); clearAiField("ingredients"); }}
                rows={6}
                placeholder={"2 tbsp olive oil\n1 onion, finely sliced\n4 eggs"}
                style={{ ...inputStyle, resize: "vertical" as const, fontFamily: "var(--font-mono, monospace)" }}
              />
            </Field>

            <Field label="Steps — one per line" error={errors.steps} aiSuggested={ai.has("steps")}>
              <textarea
                value={stepsText}
                onChange={(e) => { setStepsText(e.target.value); clearAiField("steps"); }}
                rows={6}
                placeholder={"Heat oil and soften onion.\nAdd eggs and cook until set."}
                style={{ ...inputStyle, resize: "vertical" as const }}
              />
            </Field>

            <Field label="Recipe notes" aiSuggested={ai.has("recipeNotes")}>
              <textarea
                value={recipeNotes}
                onChange={(e) => { setRecipeNotes(e.target.value); clearAiField("recipeNotes"); }}
                rows={3}
                placeholder="Tips, context, substitutions…"
                style={{ ...inputStyle, resize: "vertical" as const }}
              />
            </Field>

            {/* Trust state */}
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
              <span style={labelStyle}>Trust state</span>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                {VERIFICATION_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    style={{ display: "flex", alignItems: "center", cursor: "pointer" }}
                  >
                    <input
                      type="radio"
                      name="vs"
                      value={opt.value}
                      checked={verificationState === opt.value}
                      onChange={() => setVerificationState(opt.value)}
                      style={{ marginRight: "var(--space-2)" }}
                    />
                    <span style={{ fontSize: "var(--text-sm)", color: verificationState === opt.value ? "var(--text-primary)" : "var(--text-secondary)" }}>
                      {opt.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {saveError && (
        <p style={{ color: "var(--state-advisory)", fontSize: "var(--text-sm)" }}>{saveError}</p>
      )}

      <div style={styles.actions}>
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          style={styles.saveBtn}
        >
          {saving ? "Saving…" : `Save as ${verificationState}`}
        </button>
        <Link to="/intake" style={styles.cancelLink}>Cancel</Link>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-6)",
  },
  header: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-6)",
  },
  back: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    textDecoration: "underline",
    alignSelf: "flex-start" as const,
  },
  title: {
    fontSize: "var(--text-2xl)",
    fontWeight: 500,
    letterSpacing: "var(--tracking-tight)",
  },
  subtitle: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-relaxed)",
    maxWidth: 560,
  },
  body: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-6)",
    alignItems: "flex-start",
  } as React.CSSProperties,
  rawPanel: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
    position: "sticky" as const,
    top: "var(--space-6)",
  },
  structuredPanel: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  panelLabel: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  panelLabelText: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    fontWeight: 600,
  },
  preserved: {
    fontSize: "var(--text-xs)",
    color: "var(--state-verified)",
    letterSpacing: "var(--tracking-wide)",
  },
  rawTextarea: {
    ...{
      background: "var(--bg-field)",
      border: "1px solid var(--border-subtle)",
      borderRadius: "var(--radius-sm)",
      color: "var(--text-primary)",
      fontSize: "var(--text-sm)",
      padding: "var(--space-3)",
      width: "100%",
      resize: "vertical" as const,
      minHeight: 240,
      lineHeight: "var(--leading-relaxed)",
      fontFamily: "inherit",
    },
  } as React.CSSProperties,
  normalizeBtn: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    fontWeight: 500,
    padding: "var(--space-2) var(--space-4)",
    alignSelf: "flex-start" as const,
    letterSpacing: "var(--tracking-wide)",
  } as React.CSSProperties,
  evaluateBtn: {
    background: "none",
    border: "none",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    fontWeight: 400,
    padding: "var(--space-1) 0",
    alignSelf: "flex-start" as const,
    textDecoration: "underline",
    letterSpacing: "var(--tracking-wide)",
  } as React.CSSProperties,
  formBody: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-3)",
  } as React.CSSProperties,
  actions: {
    display: "flex",
    gap: "var(--space-4)",
    alignItems: "center",
    paddingTop: "var(--space-4)",
    borderTop: "1px solid var(--border-subtle)",
  },
  saveBtn: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-primary)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-primary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    padding: "var(--space-2) var(--space-5)",
  } as React.CSSProperties,
  cancelLink: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    textDecoration: "underline",
  },
} as const;

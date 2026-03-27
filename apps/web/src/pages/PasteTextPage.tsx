import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  approveIntakeJob,
  createIntakeJob,
  normalizeCandidate,
  updateCandidate,
} from "../lib/intake-api";
import type { CandidateOut } from "../lib/intake-api";
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

// ── Page ──────────────────────────────────────────────────────────────────────

export function PasteTextPage() {
  const navigate = useNavigate();

  // Raw source
  const [rawText, setRawText] = useState("");
  const [sourceNotes, setSourceNotes] = useState("");

  // Intake job created after first AI call or at save time
  const [jobId, setJobId] = useState<string | null>(null);

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
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  // ── AI normalize ───────────────────────────────────────────────────────────

  async function handleNormalize() {
    if (!rawText.trim()) {
      setErrors({ rawText: "Paste some source text first." });
      return;
    }
    setNormalizing(true);
    setNormalizeError(null);

    try {
      // Create the intake job if we haven't yet
      let currentJobId = jobId;
      if (!currentJobId) {
        const jobRes = await createIntakeJob("paste_text", rawText.trim(), sourceNotes.trim() || undefined);
        currentJobId = jobRes.data.id;
        setJobId(currentJobId);
      }

      const res = await normalizeCandidate(currentJobId);
      applyCandidate(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Normalization failed.";
      // Surface AI-specific errors as degraded-mode notice rather than hard failure
      if (msg.includes("ai_disabled") || msg.includes("ai_unavailable")) {
        setNormalizeError("AI normalization is unavailable. Fill in the fields manually.");
      } else {
        setNormalizeError(msg);
      }
    } finally {
      setNormalizing(false);
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

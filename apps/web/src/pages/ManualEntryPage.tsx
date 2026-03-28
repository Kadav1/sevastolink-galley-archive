import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { useSettings } from "../hooks/useSettings";
import type { VerificationState } from "../types/recipe";

// ── Form field components ─────────────────────────────────────────────────────

function Field({
  label,
  required,
  children,
  error,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  error?: string;
}) {
  return (
    <div style={fieldStyles.wrapper}>
      <label style={fieldStyles.label}>
        {label}
        {required && <span style={fieldStyles.req}> *</span>}
      </label>
      {children}
      {error && <p style={fieldStyles.error}>{error}</p>}
    </div>
  );
}

const fieldStyles = {
  wrapper: { display: "flex", flexDirection: "column" as const, gap: "var(--space-2)" },
  label: { fontSize: "var(--text-xs)", color: "var(--text-secondary)", fontWeight: 500, textTransform: "uppercase" as const, letterSpacing: "var(--tracking-wide)" },
  req: { color: "var(--state-advisory)" },
  error: { fontSize: "var(--text-xs)", color: "var(--state-advisory)" },
};

function TextInput({ value, onChange, placeholder, ...rest }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input value={value} onChange={onChange} placeholder={placeholder} style={inputStyle} {...rest} />;
}

function Select({ value, onChange, children }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select value={value} onChange={onChange} style={inputStyle}>{children}</select>;
}

const inputStyle: React.CSSProperties = {
  background: "var(--bg-field)",
  border: "1px solid var(--border-subtle)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-primary)",
  fontSize: "var(--text-sm)",
  padding: "var(--space-2) var(--space-3)",
  width: "100%",
};

// ── Dynamic ingredient rows ───────────────────────────────────────────────────

interface IngRow {
  quantity: string;
  unit: string;
  item: string;
  preparation: string;
  optional: boolean;
}

function IngredientRows({
  rows,
  onChange,
}: {
  rows: IngRow[];
  onChange: (rows: IngRow[]) => void;
}) {
  function addRow() {
    onChange([...rows, { quantity: "", unit: "", item: "", preparation: "", optional: false }]);
  }

  function updateRow(i: number, field: keyof IngRow, value: string | boolean) {
    const next = rows.map((r, idx) => (idx === i ? { ...r, [field]: value } : r));
    onChange(next);
  }

  function removeRow(i: number) {
    onChange(rows.filter((_, idx) => idx !== i));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
      {rows.map((row, i) => (
        <div key={i} style={ingRowStyles.row}>
          <input
            value={row.quantity}
            onChange={(e) => updateRow(i, "quantity", e.target.value)}
            placeholder="Qty"
            style={{ ...inputStyle, width: 60 }}
          />
          <input
            value={row.unit}
            onChange={(e) => updateRow(i, "unit", e.target.value)}
            placeholder="Unit"
            style={{ ...inputStyle, width: 70 }}
          />
          <input
            value={row.item}
            onChange={(e) => updateRow(i, "item", e.target.value)}
            placeholder="Ingredient *"
            style={{ ...inputStyle, flex: 1 }}
          />
          <input
            value={row.preparation}
            onChange={(e) => updateRow(i, "preparation", e.target.value)}
            placeholder="Prep"
            style={{ ...inputStyle, width: 110 }}
          />
          <button
            type="button"
            onClick={() => removeRow(i)}
            style={ingRowStyles.remove}
            aria-label="Remove ingredient"
          >
            ×
          </button>
        </div>
      ))}
      <button type="button" onClick={addRow} style={addBtnStyle}>
        + Add ingredient
      </button>
    </div>
  );
}

const ingRowStyles = {
  row: {
    display: "flex",
    gap: "var(--space-2)",
    alignItems: "center",
  },
  remove: {
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-base)",
    lineHeight: 1,
    padding: "0 var(--space-1)",
  } as React.CSSProperties,
};

// ── Dynamic step rows ─────────────────────────────────────────────────────────

interface StepRow {
  instruction: string;
}

function StepRows({
  rows,
  onChange,
}: {
  rows: StepRow[];
  onChange: (rows: StepRow[]) => void;
}) {
  function addRow() {
    onChange([...rows, { instruction: "" }]);
  }

  function updateRow(i: number, value: string) {
    onChange(rows.map((r, idx) => (idx === i ? { instruction: value } : r)));
  }

  function removeRow(i: number) {
    onChange(rows.filter((_, idx) => idx !== i));
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
      {rows.map((row, i) => (
        <div key={i} style={{ display: "flex", gap: "var(--space-2)", alignItems: "flex-start" }}>
          <span style={stepNumStyle}>{i + 1}</span>
          <textarea
            value={row.instruction}
            onChange={(e) => updateRow(i, e.target.value)}
            placeholder="Step instruction"
            rows={2}
            style={{ ...inputStyle, flex: 1, resize: "vertical" as const }}
          />
          <button
            type="button"
            onClick={() => removeRow(i)}
            style={ingRowStyles.remove}
            aria-label="Remove step"
          >
            ×
          </button>
        </div>
      ))}
      <button type="button" onClick={addRow} style={addBtnStyle}>
        + Add step
      </button>
    </div>
  );
}

const stepNumStyle: React.CSSProperties = {
  minWidth: 20,
  paddingTop: 6,
  textAlign: "right",
  fontSize: "var(--text-sm)",
  color: "var(--text-tertiary)",
  fontFamily: "var(--font-numeric)",
  flexShrink: 0,
};

const addBtnStyle: React.CSSProperties = {
  background: "none",
  border: "1px dashed var(--border-subtle)",
  borderRadius: "var(--radius-sm)",
  color: "var(--text-tertiary)",
  cursor: "pointer",
  fontSize: "var(--text-xs)",
  padding: "var(--space-2) var(--space-3)",
  textAlign: "left",
};

// ── Page ──────────────────────────────────────────────────────────────────────

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

const SOURCE_TYPE_OPTIONS = [
  { value: "Manual", label: "Manual" },
  { value: "Book", label: "Book" },
  { value: "Family Recipe", label: "Family Recipe" },
  { value: "Website", label: "Website" },
  { value: "Composite / Merged", label: "Composite / Merged" },
];

const VERIFICATION_OPTIONS: { value: VerificationState; label: string }[] = [
  { value: "Draft", label: "Draft — still being shaped" },
  { value: "Unverified", label: "Unverified — stored but not yet trusted" },
  { value: "Verified", label: "Verified — cooked and trusted" },
];

export function ManualEntryPage() {
  const navigate = useNavigate();
  const { data: settingsData } = useSettings();

  // Core fields
  const [title, setTitle] = useState("");
  const [shortDesc, setShortDesc] = useState("");
  const [dishRole, setDishRole] = useState("");
  const [primaryCuisine, setPrimaryCuisine] = useState("");
  const [technique, setTechnique] = useState("");
  const [servings, setServings] = useState("");
  const [prepTime, setPrepTime] = useState("");
  const [cookTime, setCookTime] = useState("");

  // Sub-resources
  const [ingredients, setIngredients] = useState<IngRow[]>([
    { quantity: "", unit: "", item: "", preparation: "", optional: false },
  ]);
  const [steps, setSteps] = useState<StepRow[]>([{ instruction: "" }]);
  const [recipeNotes, setRecipeNotes] = useState("");

  // Source
  const [sourceType, setSourceType] = useState("Manual");
  const [sourceTitle, setSourceTitle] = useState("");
  const [sourceAuthor, setSourceAuthor] = useState("");
  const [sourceNotes, setSourceNotes] = useState("");

  // Trust state — seeded from settings once loaded; user can override in-form
  const [verificationState, setVerificationState] = useState<VerificationState>("Draft");
  useEffect(() => {
    if (settingsData?.default_verification_state) {
      setVerificationState(settingsData.default_verification_state);
    }
  }, [settingsData?.default_verification_state]);

  // UI state
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  function validate(): boolean {
    const e: Record<string, string> = {};
    if (!title.trim()) e.title = "Title is required.";
    if (verificationState !== "Draft") {
      const hasIngredient = ingredients.some((i) => i.item.trim());
      const hasStep = steps.some((s) => s.instruction.trim());
      if (!hasIngredient) e.ingredients = "At least one ingredient is required for Unverified or Verified recipes.";
      if (!hasStep) e.steps = "At least one step is required for Unverified or Verified recipes.";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;

    setSaving(true);
    setSaveError(null);

    const filteredIngredients = ingredients
      .filter((i) => i.item.trim())
      .map((i, idx) => ({
        position: idx + 1,
        item: i.item.trim(),
        quantity: i.quantity.trim() || null,
        unit: i.unit.trim() || null,
        preparation: i.preparation.trim() || null,
        optional: i.optional,
      }));

    const filteredSteps = steps
      .filter((s) => s.instruction.trim())
      .map((s, idx) => ({
        position: idx + 1,
        instruction: s.instruction.trim(),
      }));

    const notes = recipeNotes.trim()
      ? [{ note_type: "recipe", content: recipeNotes.trim() }]
      : [];

    const payload = {
      title: title.trim(),
      short_description: shortDesc.trim() || null,
      dish_role: dishRole || null,
      primary_cuisine: primaryCuisine || null,
      technique_family: technique || null,
      servings: servings.trim() || null,
      prep_time_minutes: prepTime ? parseInt(prepTime, 10) : null,
      cook_time_minutes: cookTime ? parseInt(cookTime, 10) : null,
      verification_state: verificationState,
      ingredients: filteredIngredients,
      steps: filteredSteps,
      notes,
      source: {
        source_type: sourceType,
        source_title: sourceTitle.trim() || null,
        source_author: sourceAuthor.trim() || null,
        source_notes: sourceNotes.trim() || null,
      },
    };

    try {
      const result = await apiFetch<{ data: { slug: string } }>("/recipes", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      navigate(`/recipe/${result.data.slug}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Save failed.";
      setSaveError(msg);
      setSaving(false);
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <Link to="/intake" style={styles.back}>← Intake</Link>
        <h1 style={styles.title}>Manual Entry</h1>
        <p style={styles.subtitle}>Compose a recipe directly into the archive.</p>
      </header>

      <div style={styles.form}>
        {/* Core */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Recipe</h2>
          <div style={styles.grid2}>
            <div style={{ gridColumn: "1 / -1" }}>
              <Field label="Title" required error={errors.title}>
                <TextInput value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Recipe title" />
              </Field>
            </div>
            <div style={{ gridColumn: "1 / -1" }}>
              <Field label="Short description">
                <TextInput value={shortDesc} onChange={(e) => setShortDesc(e.target.value)} placeholder="One sentence (optional)" />
              </Field>
            </div>
            <Field label="Dish role">
              <Select value={dishRole} onChange={(e) => setDishRole(e.target.value)}>
                {DISH_ROLE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
              </Select>
            </Field>
            <Field label="Primary cuisine">
              <Select value={primaryCuisine} onChange={(e) => setPrimaryCuisine(e.target.value)}>
                {CUISINE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
              </Select>
            </Field>
            <Field label="Technique">
              <Select value={technique} onChange={(e) => setTechnique(e.target.value)}>
                {TECHNIQUE_OPTIONS.map((o) => <option key={o} value={o}>{o || "—"}</option>)}
              </Select>
            </Field>
            <Field label="Servings">
              <TextInput value={servings} onChange={(e) => setServings(e.target.value)} placeholder="e.g. 4" />
            </Field>
            <Field label="Prep time (min)">
              <TextInput type="number" value={prepTime} onChange={(e) => setPrepTime(e.target.value)} placeholder="20" />
            </Field>
            <Field label="Cook time (min)">
              <TextInput type="number" value={cookTime} onChange={(e) => setCookTime(e.target.value)} placeholder="45" />
            </Field>
          </div>
        </section>

        {/* Ingredients */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Ingredients</h2>
          {errors.ingredients && <p style={fieldStyles.error}>{errors.ingredients}</p>}
          <IngredientRows rows={ingredients} onChange={setIngredients} />
        </section>

        {/* Method */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Method</h2>
          {errors.steps && <p style={fieldStyles.error}>{errors.steps}</p>}
          <StepRows rows={steps} onChange={setSteps} />
        </section>

        {/* Notes */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Notes</h2>
          <Field label="Recipe notes">
            <textarea
              value={recipeNotes}
              onChange={(e) => setRecipeNotes(e.target.value)}
              rows={4}
              placeholder="Tips, variations, context…"
              style={{ ...inputStyle, resize: "vertical" as const }}
            />
          </Field>
        </section>

        {/* Source */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Source</h2>
          <div style={styles.grid2}>
            <Field label="Source type">
              <Select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
                {SOURCE_TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </Select>
            </Field>
            <Field label="Source title">
              <TextInput value={sourceTitle} onChange={(e) => setSourceTitle(e.target.value)} placeholder="Book or website name" />
            </Field>
            <Field label="Author">
              <TextInput value={sourceAuthor} onChange={(e) => setSourceAuthor(e.target.value)} placeholder="Author name" />
            </Field>
            <div style={{ gridColumn: "1 / -1" }}>
              <Field label="Source notes">
                <TextInput value={sourceNotes} onChange={(e) => setSourceNotes(e.target.value)} placeholder="Where this came from" />
              </Field>
            </div>
          </div>
        </section>

        {/* Trust state + save */}
        <section style={styles.section}>
          <h2 style={styles.sectionHeading}>Trust state</h2>
          <div style={styles.trustOptions}>
            {VERIFICATION_OPTIONS.map((opt) => (
              <label key={opt.value} style={styles.trustOption}>
                <input
                  type="radio"
                  name="verification_state"
                  value={opt.value}
                  checked={verificationState === opt.value}
                  onChange={() => setVerificationState(opt.value)}
                  style={{ marginRight: "var(--space-2)" }}
                />
                <span style={{ color: verificationState === opt.value ? "var(--text-primary)" : "var(--text-secondary)", fontSize: "var(--text-sm)" }}>
                  {opt.label}
                </span>
              </label>
            ))}
          </div>
        </section>

        {saveError && <p style={{ color: "var(--state-advisory)", fontSize: "var(--text-sm)" }}>{saveError}</p>}

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
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
    maxWidth: 760,
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
  },
  form: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
  },
  section: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  sectionHeading: {
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-3)",
  },
  grid2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-4)",
  } as React.CSSProperties,
  trustOptions: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  trustOption: {
    display: "flex",
    alignItems: "center",
    cursor: "pointer",
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

import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { IngredientList } from "../components/recipe/IngredientList";
import { MetadataStrip } from "../components/recipe/MetadataStrip";
import { NoteBlock } from "../components/recipe/NoteBlock";
import { SourcePanel } from "../components/recipe/SourcePanel";
import { StepList } from "../components/recipe/StepList";
import { StatusBadge } from "../components/ui/StatusBadge";
import { DEFAULT_SCALE, SCALE_OPTIONS, scaleServings } from "../lib/scaling";
import type { ScaleFactor } from "../lib/scaling";
import { useRecipe } from "../hooks/useRecipe";
import { useFavorite } from "../hooks/useFavorite";
import { ApiError, patchRecipe } from "../lib/api";
import { suggestMetadata, rewriteRecipe, findSimilarRecipes } from "../lib/recipe-ai-api";
import type { MetadataSuggestionOut, ArchiveRewriteOut, SimilarRecipesOut, SimilarityMatchOut } from "../lib/recipe-ai-api";

// ── Metadata suggestion panel ─────────────────────────────────────────────────

const SCALAR_FIELDS: Array<{ key: keyof MetadataSuggestionOut; label: string }> = [
  { key: "short_description", label: "Short description" },
  { key: "dish_role", label: "Dish role" },
  { key: "primary_cuisine", label: "Primary cuisine" },
  { key: "technique_family", label: "Technique family" },
  { key: "complexity", label: "Complexity" },
  { key: "time_class", label: "Time class" },
  { key: "service_format", label: "Service format" },
  { key: "season", label: "Season" },
  { key: "sector", label: "Sector" },
  { key: "class", label: "Operational class" },
  { key: "heat_window", label: "Heat window" },
];

const ARRAY_FIELDS: Array<{ key: keyof MetadataSuggestionOut; label: string }> = [
  { key: "secondary_cuisines", label: "Secondary cuisines" },
  { key: "ingredient_families", label: "Ingredient families" },
  { key: "mood_tags", label: "Mood tags" },
  { key: "storage_profile", label: "Storage profile" },
  { key: "dietary_flags", label: "Dietary flags" },
  { key: "provision_tags", label: "Provision tags" },
];

interface MetadataSuggestionPanelProps {
  suggestion: MetadataSuggestionOut;
  appliedFields: Set<string>;
  onApply: (field: string, value: unknown) => void;
  onDismiss: () => void;
}

function MetadataSuggestionPanel({
  suggestion,
  appliedFields,
  onApply,
  onDismiss,
}: MetadataSuggestionPanelProps) {
  const hasNotes =
    suggestion.confidence_notes.length > 0 || suggestion.uncertainty_notes.length > 0;

  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Metadata suggestions</span>
        <button type="button" onClick={onDismiss} style={panelStyles.dismissBtn}>
          Dismiss
        </button>
      </div>

      <div style={panelStyles.fieldList}>
        {SCALAR_FIELDS.map(({ key, label }) => {
          const val = suggestion[key] as string | null;
          if (!val) return null;
          const applied = appliedFields.has(key);
          return (
            <div key={key} style={panelStyles.fieldRow}>
              <span style={panelStyles.fieldLabel}>{label}</span>
              <span style={panelStyles.fieldValue}>{val}</span>
              <button
                type="button"
                style={applied ? panelStyles.applyBtnApplied : panelStyles.applyBtn}
                disabled={applied}
                onClick={() => onApply(key, val)}
              >
                {applied ? "Applied" : "Apply"}
              </button>
            </div>
          );
        })}

        {ARRAY_FIELDS.map(({ key, label }) => {
          const val = suggestion[key] as string[];
          if (!val || val.length === 0) return null;
          const applied = appliedFields.has(key);
          return (
            <div key={key} style={panelStyles.fieldRow}>
              <span style={panelStyles.fieldLabel}>{label}</span>
              <span style={panelStyles.fieldValue}>{val.join(", ")}</span>
              <button
                type="button"
                style={applied ? panelStyles.applyBtnApplied : panelStyles.applyBtn}
                disabled={applied}
                onClick={() => onApply(key, val)}
              >
                {applied ? "Applied" : "Apply"}
              </button>
            </div>
          );
        })}
      </div>

      {hasNotes && (
        <div style={panelStyles.notes}>
          {suggestion.confidence_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>
              {n}
            </p>
          ))}
          {suggestion.uncertainty_notes.map((n, i) => (
            <p key={i} style={{ ...panelStyles.noteItem, color: "var(--state-advisory)" }}>
              ⚠ {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Rewrite panel ─────────────────────────────────────────────────────────────

interface RewritePanelProps {
  rewrite: ArchiveRewriteOut;
  onDismiss: () => void;
}

function RewritePanel({ rewrite, onDismiss }: RewritePanelProps) {
  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Archive rewrite suggestion</span>
        <button type="button" onClick={onDismiss} style={panelStyles.dismissBtn}>
          Dismiss
        </button>
      </div>

      <p style={panelStyles.rewriteNote}>
        Read-only preview — does not modify the stored recipe.
      </p>

      {rewrite.title && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Title</span>
          <p style={panelStyles.rewriteText}>{rewrite.title}</p>
        </div>
      )}

      {rewrite.short_description && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Description</span>
          <p style={panelStyles.rewriteText}>{rewrite.short_description}</p>
        </div>
      )}

      {rewrite.ingredients.length > 0 && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Ingredients</span>
          <ul style={panelStyles.rewriteList}>
            {rewrite.ingredients.map((ing, i) => {
              const parts = [ing.amount, ing.unit, ing.item].filter(Boolean).join(" ");
              const note = ing.note ? ` — ${ing.note}` : "";
              return (
                <li key={i} style={panelStyles.rewriteListItem}>
                  {parts}
                  {note}
                  {ing.optional && " (optional)"}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {rewrite.steps.length > 0 && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Steps</span>
          <ol style={panelStyles.rewriteList}>
            {rewrite.steps.map((step) => (
              <li key={step.step_number} style={panelStyles.rewriteListItem}>
                {step.instruction}
                {step.time_note && (
                  <span style={panelStyles.rewriteMeta}> [{step.time_note}]</span>
                )}
                {step.heat_note && (
                  <span style={panelStyles.rewriteMeta}> [{step.heat_note}]</span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      {rewrite.recipe_notes && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Notes</span>
          <p style={panelStyles.rewriteText}>{rewrite.recipe_notes}</p>
        </div>
      )}

      {rewrite.service_notes && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Service notes</span>
          <p style={panelStyles.rewriteText}>{rewrite.service_notes}</p>
        </div>
      )}

      {(rewrite.rewrite_notes.length > 0 || rewrite.uncertainty_notes.length > 0) && (
        <div style={panelStyles.notes}>
          {rewrite.rewrite_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>
              {n}
            </p>
          ))}
          {rewrite.uncertainty_notes.map((n, i) => (
            <p key={i} style={{ ...panelStyles.noteItem, color: "var(--state-advisory)" }}>
              ⚠ {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Similar recipes panel ─────────────────────────────────────────────────────

const SCORE_BAND_LABEL: Record<string, string> = {
  very_high: "Very similar",
  high: "Similar",
  moderate: "Somewhat similar",
  low: "Loosely related",
};

function SimilarMatchRow({ match }: { match: SimilarityMatchOut }) {
  const bandLabel = SCORE_BAND_LABEL[match.similarity_score_band] ?? match.similarity_score_band;
  return (
    <div style={simStyles.row}>
      <div style={simStyles.rowHeader}>
        <span style={simStyles.matchTitle}>{match.title}</span>
        <span style={simStyles.band}>{bandLabel}</span>
      </div>
      <p style={simStyles.reason}>{match.primary_similarity_reason}</p>
      {match.major_differences.length > 0 && (
        <p style={simStyles.diff}>
          Differs: {match.major_differences.join("; ")}
        </p>
      )}
    </div>
  );
}

interface SimilarRecipesPanelProps {
  similar: SimilarRecipesOut;
  onDismiss: () => void;
}

function SimilarRecipesPanel({ similar, onDismiss }: SimilarRecipesPanelProps) {
  const hasMatches = similar.top_matches.length > 0 || similar.near_matches.length > 0;

  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Similar recipes</span>
        <button type="button" onClick={onDismiss} style={panelStyles.dismissBtn}>
          Dismiss
        </button>
      </div>

      {!hasMatches && (
        <p style={simStyles.empty}>No similar recipes found in the archive.</p>
      )}

      {similar.top_matches.length > 0 && (
        <div style={simStyles.group}>
          <span style={simStyles.groupLabel}>Top matches</span>
          {similar.top_matches.map((m, i) => (
            <SimilarMatchRow key={i} match={m} />
          ))}
        </div>
      )}

      {similar.near_matches.length > 0 && (
        <div style={simStyles.group}>
          <span style={simStyles.groupLabel}>Near matches</span>
          {similar.near_matches.map((m, i) => (
            <SimilarMatchRow key={i} match={m} />
          ))}
        </div>
      )}

      {similar.confidence_notes.length > 0 && (
        <div style={panelStyles.notes}>
          {similar.confidence_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>{n}</p>
          ))}
        </div>
      )}
    </div>
  );
}

const simStyles = {
  row: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    paddingBlock: "var(--space-3)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  rowHeader: {
    display: "flex",
    alignItems: "baseline",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  matchTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-primary)",
    flex: 1,
  },
  band: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    flexShrink: 0,
  },
  reason: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  diff: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  group: {
    display: "flex",
    flexDirection: "column" as const,
  },
  groupLabel: {
    fontSize: "var(--text-xs)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
    paddingBottom: "var(--space-1)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  empty: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
  },
} as const;

// ── Main page ─────────────────────────────────────────────────────────────────

export function RecipePage() {
  const { slug } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useRecipe(slug ?? "");
  const [scale, setScale] = useState<ScaleFactor>(DEFAULT_SCALE);
  const favMutation = useFavorite();

  // AI enrichment state
  const [metadata, setMetadata] = useState<MetadataSuggestionOut | null>(null);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const [metadataError, setMetadataError] = useState<string | null>(null);
  const [appliedFields, setAppliedFields] = useState<Set<string>>(new Set());
  const [rewrite, setRewrite] = useState<ArchiveRewriteOut | null>(null);
  const [rewriteLoading, setRewriteLoading] = useState(false);
  const [rewriteError, setRewriteError] = useState<string | null>(null);
  const [similar, setSimilar] = useState<SimilarRecipesOut | null>(null);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [similarError, setSimilarError] = useState<string | null>(null);

  if (isLoading) {
    return <p style={styles.state}>Loading…</p>;
  }

  if (isError || !data) {
    return <p style={styles.stateError}>Recipe not found.</p>;
  }

  const recipe = data.data;
  const aiWorking = metadataLoading || rewriteLoading || similarLoading;

  async function handleSuggestMetadata() {
    setMetadataLoading(true);
    setMetadataError(null);
    setMetadata(null);
    setAppliedFields(new Set());
    try {
      const res = await suggestMetadata(recipe.slug);
      setMetadata(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setMetadataError("AI is not available. Check LM Studio settings.");
      } else {
        setMetadataError("Metadata suggestion failed.");
      }
    } finally {
      setMetadataLoading(false);
    }
  }

  async function handleRewrite() {
    setRewriteLoading(true);
    setRewriteError(null);
    setRewrite(null);
    try {
      const res = await rewriteRecipe(recipe.slug);
      setRewrite(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setRewriteError("AI is not available. Check LM Studio settings.");
      } else {
        setRewriteError("Archive rewrite failed.");
      }
    } finally {
      setRewriteLoading(false);
    }
  }

  async function applyField(field: string, value: unknown) {
    // Map the "class" alias to "operational_class" for the PATCH body
    const patchField = field === "class" ? "operational_class" : field;
    try {
      await patchRecipe(recipe.slug, { [patchField]: value });
      await queryClient.invalidateQueries({ queryKey: ["recipe", recipe.slug] });
      setAppliedFields((prev) => new Set(prev).add(field));
    } catch {
      // silent — user can retry
    }
  }

  async function handleFindSimilar() {
    setSimilarLoading(true);
    setSimilarError(null);
    setSimilar(null);
    try {
      const res = await findSimilarRecipes(recipe.slug);
      setSimilar(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setSimilarError("AI is not available. Check LM Studio settings.");
      } else {
        setSimilarError("Similar recipe search failed.");
      }
    } finally {
      setSimilarLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      {/* Back nav */}
      <Link to="/library" style={styles.backLink} aria-label="Back to library">
        ← Library
      </Link>

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.titleRow}>
          <h1 style={styles.title}>{recipe.title}</h1>
          <div style={styles.titleMeta}>
            <StatusBadge state={recipe.verification_state} />
            <button
              type="button"
              onClick={() => {
                if (!favMutation.isPending) {
                  favMutation.mutate({ slug: recipe.slug, isFavorite: recipe.favorite });
                }
              }}
              style={{
                ...styles.favBtn,
                color: recipe.favorite ? "var(--state-favorite)" : "var(--text-tertiary)",
              }}
              aria-label={recipe.favorite ? "Remove from favourites" : "Add to favourites"}
              aria-pressed={recipe.favorite}
            >
              {recipe.favorite ? "★" : "☆"}
            </button>
          </div>
        </div>
        {recipe.short_description && (
          <p style={styles.description}>{recipe.short_description}</p>
        )}
        <div style={styles.kitchenLink}>
          <Link
            to={`/recipe/${recipe.slug}/kitchen`}
            style={styles.kitchenAnchor}
          >
            Kitchen mode →
          </Link>
        </div>
      </header>

      {/* Metadata strip */}
      <MetadataStrip recipe={recipe} />

      {/* Two-column body */}
      <div style={styles.body}>
        <div style={styles.primary}>
          {/* Scale control — only shown when recipe has parseable servings */}
          {recipe.servings && (
            <div style={styles.scaleBar} aria-label="Scale recipe">
              <span style={styles.scaleLabel}>
                {scale !== DEFAULT_SCALE
                  ? `×${scale} — ${scaleServings(recipe.servings, scale)}`
                  : recipe.servings}
              </span>
              <div style={styles.scaleOptions}>
                {SCALE_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setScale(opt.value)}
                    style={{
                      ...styles.scaleBtn,
                      ...(scale === opt.value ? styles.scaleBtnActive : {}),
                    }}
                    aria-pressed={scale === opt.value}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}
          <IngredientList ingredients={recipe.ingredients} scale={scale} />
        </div>
        <div style={styles.secondary}>
          <StepList steps={recipe.steps} scale={scale} />
        </div>
      </div>

      {/* Notes */}
      <NoteBlock notes={recipe.notes} />

      {/* Source */}
      <SourcePanel source={recipe.source} intakeJobId={recipe.intake_job_id} />

      {/* AI Tools */}
      <section style={styles.aiSection}>
        <h2 style={styles.aiSectionTitle}>AI Tools</h2>
        <div style={styles.aiActions}>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleSuggestMetadata}
            disabled={aiWorking}
          >
            {metadataLoading ? "Suggesting…" : "Suggest metadata"}
          </button>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleRewrite}
            disabled={aiWorking}
          >
            {rewriteLoading ? "Rewriting…" : "Rewrite recipe"}
          </button>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleFindSimilar}
            disabled={aiWorking}
          >
            {similarLoading ? "Searching…" : "Find similar"}
          </button>
        </div>
        {metadataError && <p style={styles.aiError}>{metadataError}</p>}
        {rewriteError && <p style={styles.aiError}>{rewriteError}</p>}
        {similarError && <p style={styles.aiError}>{similarError}</p>}
        {metadata && (
          <MetadataSuggestionPanel
            suggestion={metadata}
            appliedFields={appliedFields}
            onApply={applyField}
            onDismiss={() => setMetadata(null)}
          />
        )}
        {rewrite && (
          <RewritePanel rewrite={rewrite} onDismiss={() => setRewrite(null)} />
        )}
        {similar && (
          <SimilarRecipesPanel similar={similar} onDismiss={() => setSimilar(null)} />
        )}
      </section>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
    maxWidth: 960,
  },
  backLink: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    textDecoration: "underline",
    alignSelf: "flex-start" as const,
  },
  header: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  titleRow: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-4)",
    flexWrap: "wrap" as const,
  },
  title: {
    fontSize: "var(--text-3xl)",
    fontWeight: 500,
    letterSpacing: "var(--tracking-tight)",
    lineHeight: "var(--leading-tight)",
  },
  titleMeta: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
  },
  favBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "var(--text-lg)",
    padding: 0,
    lineHeight: 1,
    transition: "color var(--transition-fast)",
  } as React.CSSProperties,
  description: {
    fontSize: "var(--text-base)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
    maxWidth: 640,
  },
  kitchenLink: {
    marginTop: "var(--space-1)",
  },
  kitchenAnchor: {
    fontSize: "var(--text-sm)",
    color: "var(--state-info)",
    textDecoration: "underline",
  },
  body: {
    display: "flex",
    gap: "var(--space-12)",
    alignItems: "flex-start",
  },
  primary: {
    minWidth: 220,
    width: 280,
    flexShrink: 0,
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  scaleBar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "var(--space-3)",
    paddingBottom: "var(--space-3)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  scaleLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 500,
  },
  scaleOptions: {
    display: "flex",
    gap: "var(--space-1)",
  },
  scaleBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: "2px var(--space-2)",
    lineHeight: 1.4,
  } as React.CSSProperties,
  scaleBtnActive: {
    borderColor: "var(--border-primary)",
    color: "var(--text-primary)",
    background: "var(--bg-panel)",
  } as React.CSSProperties,
  secondary: {
    flex: 1,
  },
  state: {
    color: "var(--text-tertiary)",
    fontSize: "var(--text-sm)",
  },
  stateError: {
    color: "var(--state-advisory)",
    fontSize: "var(--text-sm)",
  },
  aiSection: {
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: "var(--space-6)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  aiSectionTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  aiActions: {
    display: "flex",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  aiBtn: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-4)",
  } as React.CSSProperties,
  aiError: {
    fontSize: "var(--text-sm)",
    color: "var(--state-advisory)",
  },
} as const;

const panelStyles = {
  panel: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    padding: "var(--space-5)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  panelHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  panelTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-secondary)",
  },
  dismissBtn: {
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    textDecoration: "underline",
    padding: 0,
  } as React.CSSProperties,
  fieldList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
  },
  fieldRow: {
    display: "flex",
    alignItems: "baseline",
    gap: "var(--space-3)",
    fontSize: "var(--text-sm)",
  },
  fieldLabel: {
    color: "var(--text-tertiary)",
    minWidth: 160,
    flexShrink: 0,
    fontSize: "var(--text-xs)",
  },
  fieldValue: {
    color: "var(--text-primary)",
    flex: 1,
  },
  applyBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--state-info)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: "2px var(--space-2)",
    flexShrink: 0,
  } as React.CSSProperties,
  applyBtnApplied: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "default",
    fontSize: "var(--text-xs)",
    padding: "2px var(--space-2)",
    flexShrink: 0,
  } as React.CSSProperties,
  notes: {
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: "var(--space-3)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  noteItem: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-relaxed)",
  },
  rewriteNote: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontStyle: "italic",
  },
  rewriteSection: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  rewriteLabel: {
    fontSize: "var(--text-xs)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  rewriteText: {
    fontSize: "var(--text-sm)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-relaxed)",
  },
  rewriteList: {
    margin: 0,
    paddingLeft: "var(--space-5)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  rewriteListItem: {
    fontSize: "var(--text-sm)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-relaxed)",
  },
  rewriteMeta: {
    color: "var(--text-tertiary)",
    fontSize: "var(--text-xs)",
  },
} as const;

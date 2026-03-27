import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
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

export function RecipePage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError } = useRecipe(slug ?? "");
  const [scale, setScale] = useState<ScaleFactor>(DEFAULT_SCALE);
  const favMutation = useFavorite();

  if (isLoading) {
    return <p style={styles.state}>Loading…</p>;
  }

  if (isError || !data) {
    return <p style={styles.stateError}>Recipe not found.</p>;
  }

  const recipe = data.data;

  return (
    <div style={styles.page}>
      {/* Back nav */}
      <button
        onClick={() => navigate(-1)}
        style={styles.backBtn}
        type="button"
        aria-label="Back to library"
      >
        ← Library
      </button>

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
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
    maxWidth: 960,
  },
  backBtn: {
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: 0,
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
} as const;

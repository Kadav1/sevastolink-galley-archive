import { scaleServings } from "../../lib/scaling";
import type { ScaleFactor } from "../../lib/scaling";
import type { RecipeDetail } from "../../types/recipe";

interface Props {
  recipe: RecipeDetail;
  scale: ScaleFactor;
}

export function KitchenHeader({ recipe, scale }: Props) {
  const totalTime = recipe.total_time_minutes
    ? `${recipe.total_time_minutes} min`
    : recipe.cook_time_minutes
    ? `${recipe.cook_time_minutes} min cook`
    : recipe.prep_time_minutes
    ? `${recipe.prep_time_minutes} min prep`
    : null;

  const servingsDisplay = recipe.servings
    ? scaleServings(recipe.servings, scale)
    : null;

  return (
    <header style={styles.header}>
      <h1 style={styles.title}>{recipe.title}</h1>

      {recipe.short_description && (
        <p style={styles.description}>{recipe.short_description}</p>
      )}

      {/* Minimal cooking-relevant metadata only */}
      {(servingsDisplay || totalTime || recipe.heat_window) && (
        <div style={styles.metaRow} aria-label="Key recipe info">
          {servingsDisplay && (
            <span style={styles.metaItem}>
              <span style={styles.metaLabel}>Serves</span>
              <span style={styles.metaValue}>
                {servingsDisplay}
                {scale !== 1 && (
                  <span style={styles.scaleIndicator}> ×{scale}</span>
                )}
              </span>
            </span>
          )}
          {totalTime && (
            <span style={styles.metaItem}>
              <span style={styles.metaLabel}>Time</span>
              <span style={styles.metaValue}>{totalTime}</span>
            </span>
          )}
          {recipe.heat_window && (
            <span style={styles.metaItem}>
              <span style={styles.metaLabel}>Heat</span>
              <span style={styles.metaValue}>{recipe.heat_window}</span>
            </span>
          )}
        </div>
      )}
    </header>
  );
}

const styles = {
  header: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-8)",
  },
  title: {
    fontSize: "var(--text-3xl)",
    fontWeight: 500,
    letterSpacing: "var(--tracking-tight)",
    lineHeight: "var(--leading-tight)",
    color: "var(--text-primary)",
  },
  description: {
    fontSize: "var(--text-base)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  metaRow: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "var(--space-6)",
  },
  metaItem: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  metaLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 500,
    textTransform: "uppercase" as const,
    letterSpacing: "var(--tracking-wide)",
  },
  metaValue: {
    fontSize: "var(--text-lg)",
    color: "var(--text-primary)",
    fontWeight: 400,
    lineHeight: "var(--leading-snug)",
  },
  scaleIndicator: {
    fontSize: "var(--text-sm)",
    color: "var(--state-advisory)",
    fontWeight: 400,
  },
} as const;

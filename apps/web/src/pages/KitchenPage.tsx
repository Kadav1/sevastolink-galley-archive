import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { KitchenHeader } from "../components/kitchen/KitchenHeader";
import { KitchenIngredients } from "../components/kitchen/KitchenIngredients";
import { KitchenSteps } from "../components/kitchen/KitchenSteps";
import { DEFAULT_SCALE, SCALE_OPTIONS } from "../lib/scaling";
import type { ScaleFactor } from "../lib/scaling";
import { useRecipe } from "../hooks/useRecipe";

// Re-export for any legacy imports
export type { ScaleFactor };

export function KitchenPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data, isLoading, isError } = useRecipe(slug ?? "");
  const [scale, setScale] = useState<ScaleFactor>(DEFAULT_SCALE);

  // ── Loading ──────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div data-mode="kitchen" style={styles.page}>
        <p style={styles.stateMsg}>Loading…</p>
      </div>
    );
  }

  // ── Error / not found ────────────────────────────────────────────────────

  if (isError || !data) {
    return (
      <div data-mode="kitchen" style={styles.page}>
        <Link to="/library" style={styles.exitLink}>← Library</Link>
        <p style={styles.stateError}>Recipe not found.</p>
      </div>
    );
  }

  const recipe = data.data;

  return (
    <div data-mode="kitchen" style={styles.page}>

      {/* Exit bar */}
      <div style={styles.exitBar}>
        <Link to={`/recipe/${recipe.slug}`} style={styles.exitLink}>
          ← Recipe
        </Link>
      </div>

      {/* Kitchen header: title + key metadata */}
      <KitchenHeader recipe={recipe} scale={scale} />

      {/* Scale controls */}
      {recipe.servings && (
        <div style={styles.scaleRow} aria-label="Serving scale">
          <span style={styles.scaleLabel}>Scale</span>
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

      {/* Ingredients */}
      <KitchenIngredients ingredients={recipe.ingredients} scale={scale} />

      {/* Steps */}
      <KitchenSteps steps={recipe.steps} scale={scale} />

      {/* Service notes — surface the recipe notes if present */}
      {recipe.notes.length > 0 && (
        <section style={styles.notesSection} aria-label="Notes">
          <h2 style={styles.sectionLabel}>Notes</h2>
          {recipe.notes.map((note) => (
            <p key={note.id} style={styles.noteText}>{note.content}</p>
          ))}
        </section>
      )}

      {/* Bottom exit */}
      <div style={styles.bottomExit}>
        <Link to={`/recipe/${recipe.slug}`} style={styles.exitLinkBottom}>
          ← Back to full recipe
        </Link>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100dvh",
    background: "var(--bg-base)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-10)",
    padding: "var(--space-8) var(--space-8) var(--space-16)",
    maxWidth: 720,
    margin: "0 auto",
    boxSizing: "border-box" as const,
    width: "100%",
  },
  exitBar: {
    paddingTop: "var(--space-2)",
  },
  exitLink: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    textDecoration: "none",
  },
  exitLinkBottom: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    textDecoration: "underline",
  },
  scaleRow: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-4)",
    marginTop: "calc(-1 * var(--space-6))",
  },
  scaleLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 500,
    textTransform: "uppercase" as const,
    letterSpacing: "var(--tracking-wide)",
  },
  scaleOptions: {
    display: "flex",
    gap: "var(--space-2)",
  },
  scaleBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-1) var(--space-3)",
    transition: "var(--transition-fast)",
  } as React.CSSProperties,
  scaleBtnActive: {
    borderColor: "var(--border-primary)",
    color: "var(--text-primary)",
    background: "var(--bg-panel)",
  } as React.CSSProperties,
  notesSection: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: "var(--space-8)",
  },
  sectionLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 600,
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
  },
  noteText: {
    fontSize: "var(--text-base)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  bottomExit: {
    paddingTop: "var(--space-8)",
    borderTop: "1px solid var(--border-subtle)",
  },
  stateMsg: {
    color: "var(--text-tertiary)",
    fontSize: "var(--text-base)",
  },
  stateError: {
    color: "var(--state-advisory)",
    fontSize: "var(--text-base)",
    marginTop: "var(--space-8)",
  },
} as const;

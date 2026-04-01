/**
 * MetadataStrip — Recipe Detail metadata panel.
 *
 * Field hierarchy:
 *   Primary (cooking-utility): Serves, Time, Heat — most immediately useful
 *   Secondary (classification): Role, Cuisine, Technique, Complexity — browse/context
 *   Status: Trust state — archive signal, visually separated
 *
 * Omitted from strip: Sector, operational_class (archival overlay — low cooking utility)
 */

import type { RecipeDetail } from "../../types/recipe";
import { MetaItem } from "../ui/MetaItem";
import { StatusBadge } from "../ui/StatusBadge";

interface Props {
  recipe: RecipeDetail;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function MetadataStrip({ recipe }: Props) {
  // Time: prefer total; fall back to prep+cook individually; fall back to time_class label
  const totalTime = recipe.total_time_minutes
    ? `${recipe.total_time_minutes} min`
    : null;
  const prepTime = recipe.prep_time_minutes
    ? `${recipe.prep_time_minutes} min prep`
    : null;
  const cookTime = recipe.cook_time_minutes
    ? `${recipe.cook_time_minutes} min cook`
    : null;
  const timeDisplay = totalTime
    ?? (prepTime && cookTime ? `${recipe.prep_time_minutes! + recipe.cook_time_minutes!} min` : null)
    ?? prepTime
    ?? cookTime
    ?? (recipe.time_class ?? null);

  // Primary group: any cooking-utility field that is present
  const hasPrimary = recipe.servings || timeDisplay || recipe.heat_window;

  // Secondary group: classification fields
  const hasSecondary =
    recipe.dish_role || recipe.primary_cuisine || recipe.technique_family || recipe.complexity;

  if (!hasPrimary && !hasSecondary) {
    // Only trust state — render minimal strip
    return (
      <div style={styles.strip} aria-label="Recipe metadata">
        <div style={styles.statusGroup}>
          <span style={labelStyle}>Trust</span>
          <StatusBadge state={recipe.verification_state} />
        </div>
      </div>
    );
  }

  return (
    <div style={styles.strip} aria-label="Recipe metadata">
      {/* Primary group */}
      {hasPrimary && (
        <div style={styles.primaryGroup}>
          <MetaItem label="Serves" value={recipe.servings} size="base" style={styles.primaryItem} />
          <MetaItem label="Time" value={timeDisplay} size="base" style={styles.primaryItem} />
          <MetaItem label="Heat" value={recipe.heat_window} size="base" style={styles.primaryItem} />
        </div>
      )}

      {/* Secondary group */}
      {hasSecondary && (
        <div style={styles.secondaryGroup}>
          <MetaItem label="Role" value={recipe.dish_role} size="sm" style={styles.secondaryItem} />
          <MetaItem label="Cuisine" value={recipe.primary_cuisine} size="sm" style={styles.secondaryItem} />
          <MetaItem label="Technique" value={recipe.technique_family} size="sm" style={styles.secondaryItem} />
          <MetaItem label="Complexity" value={recipe.complexity} size="sm" style={styles.secondaryItem} />
        </div>
      )}

      {/* Status */}
      <div style={styles.statusGroup}>
        <span style={labelStyle}>Trust</span>
        <StatusBadge state={recipe.verification_state} />
      </div>
    </div>
  );
}

const styles = {
  strip: {
    display: "flex",
    flexWrap: "wrap" as const,
    alignItems: "stretch",
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    overflow: "hidden",
    gap: 0,
  },
  // Primary: cooking-utility fields — slightly larger value text
  primaryGroup: {
    display: "flex",
    flexWrap: "wrap" as const,
    borderRight: "1px solid var(--border-subtle)",
  },
  // Item padding + border — passed as style override to MetaItem
  primaryItem: {
    padding: "var(--space-3) var(--space-5)",
    borderRight: "1px solid var(--border-subtle)",
  },
  // Secondary: classification fields — smaller, quieter
  secondaryGroup: {
    display: "flex",
    flexWrap: "wrap" as const,
    borderRight: "1px solid var(--border-subtle)",
  },
  secondaryItem: {
    padding: "var(--space-3) var(--space-4)",
    borderRight: "1px solid var(--border-subtle)",
  },
  // Status group — trust badge
  statusGroup: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "var(--space-3) var(--space-4)",
    justifyContent: "center",
  },
} as const;

// Shared label style — matches MetaItem's internal labelStyle
const labelStyle = {
  fontSize: "var(--text-xs)",
  color: "var(--text-tertiary)",
  letterSpacing: "var(--tracking-wide)",
  textTransform: "uppercase" as const,
  fontWeight: 500,
} as const;

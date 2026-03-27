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
import { StatusBadge } from "../ui/StatusBadge";

interface Props {
  recipe: RecipeDetail;
}

// ── Internal sub-components ───────────────────────────────────────────────────

function PrimaryItem({
  label,
  value,
}: {
  label: string;
  value: string | null | undefined;
}) {
  if (!value) return null;
  return (
    <div style={styles.primaryItem}>
      <span style={styles.itemLabel}>{label}</span>
      <span style={styles.primaryValue}>{value}</span>
    </div>
  );
}

function SecondaryItem({
  label,
  value,
}: {
  label: string;
  value: string | null | undefined;
}) {
  if (!value) return null;
  return (
    <div style={styles.secondaryItem}>
      <span style={styles.itemLabel}>{label}</span>
      <span style={styles.secondaryValue}>{value}</span>
    </div>
  );
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
          <span style={styles.itemLabel}>Trust</span>
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
          <PrimaryItem label="Serves" value={recipe.servings} />
          <PrimaryItem label="Time" value={timeDisplay} />
          <PrimaryItem label="Heat" value={recipe.heat_window} />
        </div>
      )}

      {/* Secondary group */}
      {hasSecondary && (
        <div style={styles.secondaryGroup}>
          <SecondaryItem label="Role" value={recipe.dish_role} />
          <SecondaryItem label="Cuisine" value={recipe.primary_cuisine} />
          <SecondaryItem label="Technique" value={recipe.technique_family} />
          <SecondaryItem label="Complexity" value={recipe.complexity} />
        </div>
      )}

      {/* Status */}
      <div style={styles.statusGroup}>
        <span style={styles.itemLabel}>Trust</span>
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
  primaryItem: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "var(--space-3) var(--space-5)",
    borderRight: "1px solid var(--border-subtle)",
  },
  primaryValue: {
    fontSize: "var(--text-base)",
    color: "var(--text-primary)",
    fontWeight: 400,
    lineHeight: "var(--leading-snug)",
  },
  // Secondary: classification fields — smaller, quieter
  secondaryGroup: {
    display: "flex",
    flexWrap: "wrap" as const,
    borderRight: "1px solid var(--border-subtle)",
  },
  secondaryItem: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "var(--space-3) var(--space-4)",
    borderRight: "1px solid var(--border-subtle)",
  },
  secondaryValue: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    fontWeight: 400,
    lineHeight: "var(--leading-snug)",
  },
  // Status group — trust badge
  statusGroup: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    padding: "var(--space-3) var(--space-4)",
    justifyContent: "center",
  },
  // Shared label style
  itemLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
    fontWeight: 500,
  },
} as const;

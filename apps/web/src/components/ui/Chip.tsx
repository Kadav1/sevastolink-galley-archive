/**
 * Chip — compact inline tag for taxonomy facets and filter displays.
 *
 * States:
 *   passive  — quiet; used for displaying classification tags on recipe cards
 *   active   — highlighted; used for active filter selections
 *   removable — active + shows × dismiss button (onRemove required)
 *
 * Usage:
 *   <Chip>Vegetarian</Chip>
 *   <Chip active>Italian</Chip>
 *   <Chip active onRemove={() => clearFilter("Italian")}>Italian</Chip>
 */

import type { CSSProperties } from "react";

interface Props {
  children: React.ReactNode;
  active?: boolean;
  onRemove?: () => void;
  style?: CSSProperties;
}

export function Chip({ children, active = false, onRemove, style }: Props) {
  return (
    <span
      style={{
        ...chip,
        ...(active ? chipActive : chipPassive),
        ...style,
      }}
    >
      {children}
      {onRemove && (
        <button
          type="button"
          style={removeBtn}
          onClick={onRemove}
          aria-label={`Remove ${String(children)}`}
        >
          ×
        </button>
      )}
    </span>
  );
}

const chip: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: "var(--space-1)",
  padding: "3px var(--space-2)",
  borderRadius: "var(--radius-sm)",
  fontSize: "var(--text-xs)",
  fontWeight: 400,
  letterSpacing: "var(--tracking-normal)",
  lineHeight: 1.4,
  whiteSpace: "nowrap",
};

const chipPassive: CSSProperties = {
  background: "var(--bg-field)",
  color: "var(--text-tertiary)",
  border: "1px solid var(--border-subtle)",
};

const chipActive: CSSProperties = {
  background: "var(--bg-overlay)",
  color: "var(--text-secondary)",
  border: "1px solid var(--border-primary)",
};

const removeBtn: CSSProperties = {
  background: "none",
  border: "none",
  cursor: "pointer",
  color: "inherit",
  padding: 0,
  lineHeight: 1,
  fontSize: "var(--text-sm)",
  opacity: 0.7,
};

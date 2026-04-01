/**
 * Badge — general-purpose small text label.
 *
 * Use for classification labels (complexity, cuisine, dietary flags, etc.)
 * that are not verification states. For verification states use StatusBadge.
 *
 * Variants:
 *   default  — quiet panel background, secondary text
 *   info     — blue-grey tint (quiet system cues)
 *   advisory — amber tint (AI suggestions, review states)
 *   muted    — near-invisible, archived-palette background
 */

import type { CSSProperties } from "react";

export type BadgeVariant = "default" | "info" | "advisory" | "muted";

interface Props {
  children: React.ReactNode;
  variant?: BadgeVariant;
  style?: CSSProperties;
}

const VARIANT_STYLES: Record<BadgeVariant, CSSProperties> = {
  default: {
    background: "var(--bg-panel)",
    color: "var(--text-secondary)",
    border: "1px solid var(--border-subtle)",
  },
  info: {
    background: "rgba(92, 122, 138, 0.15)",
    color: "var(--state-info)",
    border: "none",
  },
  advisory: {
    background: "var(--state-advisory-bg)",
    color: "var(--state-advisory)",
    border: "none",
  },
  muted: {
    background: "var(--state-archived-bg)",
    color: "var(--text-tertiary)",
    border: "none",
  },
};

export function Badge({ children, variant = "default", style }: Props) {
  return (
    <span
      style={{
        ...badge,
        ...VARIANT_STYLES[variant],
        ...style,
      }}
    >
      {children}
    </span>
  );
}

const badge: CSSProperties = {
  display: "inline-block",
  padding: "2px var(--space-2)",
  borderRadius: "var(--radius-sm)",
  fontSize: "var(--text-xs)",
  fontWeight: 500,
  letterSpacing: "var(--tracking-wide)",
  textTransform: "uppercase",
  lineHeight: 1.4,
  whiteSpace: "nowrap",
};

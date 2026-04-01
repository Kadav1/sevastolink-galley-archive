/**
 * MetaItem — label / value pair for metadata strips and context panels.
 *
 * Renders a stacked (label above, value below) pair used throughout:
 *   - MetadataStrip primary and secondary groups
 *   - AI panels (confidence notes, field previews)
 *   - Kitchen mode metadata
 *
 * Sizes:
 *   base — primary cooking-utility fields (Serves, Time, Heat)
 *   sm   — classification fields (Role, Cuisine, Technique, Complexity)
 *
 * Returns null when value is falsy so callers don't need conditional guards.
 */

import type { CSSProperties } from "react";

interface Props {
  label: string;
  value: string | null | undefined;
  size?: "base" | "sm";
  style?: CSSProperties;
}

export function MetaItem({ label, value, size = "base", style }: Props) {
  if (!value) return null;
  return (
    <div style={{ ...item, ...style }}>
      <span style={labelStyle}>{label}</span>
      <span style={size === "base" ? valueBase : valueSm}>{value}</span>
    </div>
  );
}

const item: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-1)",
};

const labelStyle: CSSProperties = {
  fontSize: "var(--text-xs)",
  color: "var(--text-tertiary)",
  letterSpacing: "var(--tracking-wide)",
  textTransform: "uppercase",
  fontWeight: 500,
};

const valueBase: CSSProperties = {
  fontSize: "var(--text-base)",
  color: "var(--text-primary)",
  fontWeight: 400,
  lineHeight: "var(--leading-snug)",
};

const valueSm: CSSProperties = {
  fontSize: "var(--text-sm)",
  color: "var(--text-secondary)",
  fontWeight: 400,
  lineHeight: "var(--leading-snug)",
};

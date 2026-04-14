// Shared styles for AI result panels (MetadataSuggestionPanel, RewritePanel, SimilarRecipesPanel).
import type React from "react";

export const panelStyles = {
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

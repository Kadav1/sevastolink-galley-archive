import { useState } from "react";
import type { Source } from "../../types/recipe";

interface Props {
  source: Source | null;
  intakeJobId?: string | null;
}

export function SourcePanel({ source, intakeJobId }: Props) {
  const [showRaw, setShowRaw] = useState(false);

  if (!source && !intakeJobId) return null;

  return (
    <section style={styles.section} aria-label="Source and provenance">
      <h2 style={styles.heading}>Source</h2>
      <div style={styles.panel}>
        {source ? (
          <>
            <div style={styles.row}>
              <span style={styles.label}>Type</span>
              <span style={styles.value}>{source.source_type}</span>
            </div>
            {source.source_title && (
              <div style={styles.row}>
                <span style={styles.label}>Title</span>
                <span style={styles.value}>{source.source_title}</span>
              </div>
            )}
            {source.source_author && (
              <div style={styles.row}>
                <span style={styles.label}>Author</span>
                <span style={styles.value}>{source.source_author}</span>
              </div>
            )}
            {source.source_url && (
              <div style={styles.row}>
                <span style={styles.label}>URL</span>
                <a
                  href={source.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.link}
                >
                  {source.source_url}
                </a>
              </div>
            )}
            {source.source_notes && (
              <div style={styles.row}>
                <span style={styles.label}>Notes</span>
                <span style={styles.value}>{source.source_notes}</span>
              </div>
            )}
            {source.raw_source_text && (
              <div style={styles.rawWrapper}>
                <button
                  onClick={() => setShowRaw((v) => !v)}
                  style={styles.toggleBtn}
                  type="button"
                >
                  {showRaw ? "Hide" : "Show"} raw source text
                </button>
                {showRaw && (
                  <pre style={styles.raw}>{source.raw_source_text}</pre>
                )}
              </div>
            )}
          </>
        ) : (
          <p style={styles.none}>No source recorded.</p>
        )}
      </div>
    </section>
  );
}

const styles = {
  section: { display: "flex", flexDirection: "column" as const, gap: "var(--space-4)" },
  heading: {
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-3)",
  },
  panel: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    padding: "var(--space-4)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  row: { display: "flex", gap: "var(--space-4)", alignItems: "flex-start" },
  label: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
    minWidth: 60,
    paddingTop: 2,
    flexShrink: 0,
  },
  value: { fontSize: "var(--text-sm)", color: "var(--text-secondary)" },
  link: {
    fontSize: "var(--text-sm)",
    color: "var(--state-info)",
    textDecoration: "underline",
    wordBreak: "break-all" as const,
  },
  rawWrapper: { display: "flex", flexDirection: "column" as const, gap: "var(--space-2)", marginTop: "var(--space-2)" },
  toggleBtn: {
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: 0,
    textDecoration: "underline",
    textAlign: "left" as const,
  },
  raw: {
    background: "var(--bg-field)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    padding: "var(--space-4)",
    fontSize: "var(--text-xs)",
    color: "var(--text-secondary)",
    whiteSpace: "pre-wrap" as const,
    wordBreak: "break-word" as const,
    maxHeight: 300,
    overflow: "auto",
  },
  none: { fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
} as const;

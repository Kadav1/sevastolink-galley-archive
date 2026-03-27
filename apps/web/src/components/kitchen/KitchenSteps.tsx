import { useState } from "react";
import { scaleStepText } from "../../lib/scaling";
import type { ScaleFactor } from "../../lib/scaling";
import type { Step } from "../../types/recipe";

interface Props {
  steps: Step[];
  scale: ScaleFactor;
}

export function KitchenSteps({ steps, scale }: Props) {
  const [done, setDone] = useState<Set<number>>(new Set());

  function toggle(position: number) {
    setDone((prev) => {
      const next = new Set(prev);
      if (next.has(position)) next.delete(position);
      else next.add(position);
      return next;
    });
  }

  if (steps.length === 0) {
    return (
      <section style={styles.section} aria-label="Method">
        <h2 style={styles.sectionLabel}>Method</h2>
        <p style={styles.empty}>No method recorded.</p>
      </section>
    );
  }

  return (
    <section style={styles.section} aria-label="Method">
      <h2 style={styles.sectionLabel}>Method</h2>
      <ol style={styles.list}>
        {steps.map((step) => {
          const isDone = done.has(step.position);
          return (
            <li
              key={step.id}
              style={styles.item}
              onClick={() => toggle(step.position)}
              aria-label={isDone ? `Step ${step.position} — done. Tap to undo.` : `Step ${step.position}. Tap to mark done.`}
            >
              <span
                style={{
                  ...styles.number,
                  ...(isDone ? styles.numberDone : {}),
                }}
                aria-hidden="true"
              >
                {isDone ? "✓" : step.position}
              </span>
              <div
                style={{
                  ...styles.content,
                  ...(isDone ? styles.contentDone : {}),
                }}
              >
                <p style={styles.instruction}>{scaleStepText(step.instruction, scale).text}</p>
                {(step.time_note || step.equipment_note) && (
                  <p style={styles.annotation}>
                    {[step.time_note, step.equipment_note]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

const styles = {
  section: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-6)",
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
  list: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-10)",
    paddingLeft: 0,
    listStyle: "none",
  },
  item: {
    display: "grid",
    gridTemplateColumns: "2rem 1fr",
    gap: "var(--space-4)",
    alignItems: "start",
    cursor: "pointer",
  } as React.CSSProperties,
  number: {
    fontSize: "var(--text-lg)",
    color: "var(--text-tertiary)",
    fontWeight: 500,
    lineHeight: "var(--leading-tight)",
    paddingTop: "0.1em",
    textAlign: "right" as const,
    fontVariantNumeric: "tabular-nums",
    transition: "color var(--transition-fast)",
  } as React.CSSProperties,
  numberDone: {
    color: "var(--state-verified)",
  } as React.CSSProperties,
  content: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
    transition: "opacity var(--transition-normal)",
  },
  contentDone: {
    opacity: 0.4,
  } as React.CSSProperties,
  instruction: {
    fontSize: "var(--text-lg)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-relaxed)",
    fontWeight: 400,
  },
  annotation: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-normal)",
    fontStyle: "italic",
  },
  empty: {
    fontSize: "var(--text-base)",
    color: "var(--text-tertiary)",
  },
} as const;

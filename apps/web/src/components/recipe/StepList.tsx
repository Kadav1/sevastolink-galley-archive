import { scaleStepText } from "../../lib/scaling";
import type { ScaleFactor } from "../../lib/scaling";
import type { Step } from "../../types/recipe";

interface Props {
  steps: Step[];
  scale: ScaleFactor;
}

export function StepList({ steps, scale }: Props) {
  if (steps.length === 0) {
    return <p style={styles.empty}>No method recorded.</p>;
  }

  return (
    <section style={styles.section} aria-label="Method">
      <h2 style={styles.heading}>Method</h2>
      <ol style={styles.list}>
        {steps.map((step) => {
          const { text } = scaleStepText(step.instruction, scale);
          return (
            <li key={step.id} style={styles.item}>
              <span style={styles.number}>{step.position}</span>
              <div style={styles.content}>
                <p style={styles.instruction}>{text}</p>
                {(step.time_note || step.equipment_note) && (
                  <p style={styles.note}>
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
    gap: "var(--space-4)",
  },
  heading: {
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-3)",
  },
  list: { display: "flex", flexDirection: "column" as const, gap: "var(--space-6)", paddingLeft: 0, listStyle: "none" },
  item: {
    display: "flex",
    gap: "var(--space-4)",
    alignItems: "flex-start",
  },
  number: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    fontFamily: "var(--font-numeric)",
    fontWeight: 500,
    minWidth: 20,
    paddingTop: 2,
    flexShrink: 0,
    textAlign: "right" as const,
  },
  content: { flex: 1, display: "flex", flexDirection: "column" as const, gap: "var(--space-2)" },
  instruction: {
    fontSize: "var(--text-base)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-relaxed)",
  },
  note: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    fontStyle: "italic",
  },
  empty: { fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
} as const;

import type { VerificationState } from "../../types/recipe";

const STATE_STYLES: Record<
  VerificationState,
  { bg: string; color: string; label: string }
> = {
  Verified: {
    bg: "var(--state-verified-bg)",
    color: "var(--state-verified)",
    label: "Verified",
  },
  Unverified: {
    bg: "var(--state-advisory-bg)",
    color: "var(--state-advisory)",
    label: "Unverified",
  },
  Draft: {
    bg: "var(--state-archived-bg)",
    color: "var(--text-tertiary)",
    label: "Draft",
  },
  Archived: {
    bg: "var(--state-archived-bg)",
    color: "var(--state-archived)",
    label: "Archived",
  },
};

interface Props {
  state: VerificationState;
}

export function StatusBadge({ state }: Props) {
  const s = STATE_STYLES[state] ?? STATE_STYLES.Draft;
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px var(--space-2)",
        borderRadius: "var(--radius-sm)",
        fontSize: "var(--text-xs)",
        fontWeight: 500,
        letterSpacing: "var(--tracking-wide)",
        textTransform: "uppercase",
        background: s.bg,
        color: s.color,
      }}
      aria-label={`Verification state: ${s.label}`}
    >
      {s.label}
    </span>
  );
}

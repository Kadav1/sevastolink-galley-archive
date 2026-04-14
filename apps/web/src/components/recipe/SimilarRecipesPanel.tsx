import type {
  SimilarRecipesOut,
  SimilarityMatchOut,
} from "../../lib/recipe-ai-api";
import { panelStyles } from "./aiPanelStyles";

const SCORE_BAND_LABEL: Record<string, string> = {
  very_high: "Very similar",
  high: "Similar",
  moderate: "Somewhat similar",
  low: "Loosely related",
};

const simStyles = {
  row: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    paddingBlock: "var(--space-3)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  rowHeader: {
    display: "flex",
    alignItems: "baseline",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  matchTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-primary)",
    flex: 1,
  },
  band: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    flexShrink: 0,
  },
  reason: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  diff: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  group: {
    display: "flex",
    flexDirection: "column" as const,
  },
  groupLabel: {
    fontSize: "var(--text-xs)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
    paddingBottom: "var(--space-1)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  empty: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
  },
} as const;

function SimilarMatchRow({ match }: { match: SimilarityMatchOut }) {
  const bandLabel =
    SCORE_BAND_LABEL[match.similarity_score_band] ??
    match.similarity_score_band;
  return (
    <div style={simStyles.row}>
      <div style={simStyles.rowHeader}>
        <span style={simStyles.matchTitle}>{match.title}</span>
        <span style={simStyles.band}>{bandLabel}</span>
      </div>
      <p style={simStyles.reason}>{match.primary_similarity_reason}</p>
      {match.major_differences.length > 0 && (
        <p style={simStyles.diff}>
          Differs: {match.major_differences.join("; ")}
        </p>
      )}
    </div>
  );
}

export interface SimilarRecipesPanelProps {
  similar: SimilarRecipesOut;
  onDismiss: () => void;
}

export function SimilarRecipesPanel({
  similar,
  onDismiss,
}: SimilarRecipesPanelProps) {
  const hasMatches =
    similar.top_matches.length > 0 || similar.near_matches.length > 0;

  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Similar recipes</span>
        <button
          type="button"
          onClick={onDismiss}
          style={panelStyles.dismissBtn}
        >
          Dismiss
        </button>
      </div>

      {!hasMatches && (
        <p style={simStyles.empty}>No similar recipes found in the archive.</p>
      )}

      {similar.top_matches.length > 0 && (
        <div style={simStyles.group}>
          <span style={simStyles.groupLabel}>Top matches</span>
          {similar.top_matches.map((m, i) => (
            <SimilarMatchRow key={i} match={m} />
          ))}
        </div>
      )}

      {similar.near_matches.length > 0 && (
        <div style={simStyles.group}>
          <span style={simStyles.groupLabel}>Near matches</span>
          {similar.near_matches.map((m, i) => (
            <SimilarMatchRow key={i} match={m} />
          ))}
        </div>
      )}

      {similar.confidence_notes.length > 0 && (
        <div style={panelStyles.notes}>
          {similar.confidence_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>
              {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

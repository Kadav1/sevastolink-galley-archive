import { useState } from "react";
import { ApiError } from "../lib/api";
import { suggestPantry } from "../lib/recipe-ai-api";
import type { PantryMatchOut, PantrySuggestionOut } from "../lib/recipe-ai-api";

// ── Match card ────────────────────────────────────────────────────────────────

function MatchCard({ match, band }: { match: PantryMatchOut; band: "direct" | "near" }) {
  return (
    <div style={cardStyles.card}>
      <div style={cardStyles.header}>
        <span style={cardStyles.title}>{match.title}</span>
        <span style={band === "direct" ? cardStyles.bandDirect : cardStyles.bandNear}>
          {band === "direct" ? "Direct match" : "Near match"}
        </span>
      </div>
      <p style={cardStyles.reason}>{match.why_it_matches}</p>
      {match.missing_items.length > 0 && (
        <p style={cardStyles.missing}>
          Missing: {match.missing_items.join(", ")}
        </p>
      )}
      {match.recommended_adjustments.length > 0 && (
        <ul style={cardStyles.adjustments}>
          {match.recommended_adjustments.map((a, i) => (
            <li key={i} style={cardStyles.adjustmentItem}>
              {a}
            </li>
          ))}
        </ul>
      )}
      {match.time_fit && <p style={cardStyles.timeFit}>{match.time_fit}</p>}
    </div>
  );
}

const cardStyles = {
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    padding: "var(--space-4)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
  },
  header: {
    display: "flex",
    alignItems: "baseline",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  title: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-primary)",
    flex: 1,
  },
  bandDirect: {
    fontSize: "var(--text-xs)",
    color: "var(--state-verified)",
    flexShrink: 0,
  },
  bandNear: {
    fontSize: "var(--text-xs)",
    color: "var(--state-advisory)",
    flexShrink: 0,
  },
  reason: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  missing: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  adjustments: {
    margin: 0,
    paddingLeft: "var(--space-4)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  adjustmentItem: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  timeFit: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontStyle: "italic",
  },
} as const;

// ── Results ───────────────────────────────────────────────────────────────────

function Results({ result }: { result: PantrySuggestionOut }) {
  const hasMatches =
    result.direct_matches.length > 0 || result.near_matches.length > 0;
  const hasIdeas = result.quick_ideas.length > 0;
  const hasNotes =
    result.pantry_gap_notes.length > 0 ||
    result.substitution_suggestions.length > 0 ||
    result.confidence_notes.length > 0;

  return (
    <div style={resultStyles.container}>
      {!hasMatches && !hasIdeas && (
        <p style={resultStyles.empty}>
          No matches found. Try adding more ingredients.
        </p>
      )}

      {result.direct_matches.length > 0 && (
        <section style={resultStyles.section}>
          <h3 style={resultStyles.sectionTitle}>Direct matches</h3>
          <div style={resultStyles.grid}>
            {result.direct_matches.map((m, i) => (
              <MatchCard key={i} match={m} band="direct" />
            ))}
          </div>
        </section>
      )}

      {result.near_matches.length > 0 && (
        <section style={resultStyles.section}>
          <h3 style={resultStyles.sectionTitle}>Near matches</h3>
          <div style={resultStyles.grid}>
            {result.near_matches.map((m, i) => (
              <MatchCard key={i} match={m} band="near" />
            ))}
          </div>
        </section>
      )}

      {hasIdeas && (
        <section style={resultStyles.section}>
          <h3 style={resultStyles.sectionTitle}>Quick ideas</h3>
          <ul style={resultStyles.ideaList}>
            {result.quick_ideas.map((idea, i) => (
              <li key={i} style={resultStyles.ideaItem}>
                {idea}
              </li>
            ))}
          </ul>
        </section>
      )}

      {hasNotes && (
        <section style={resultStyles.notesSection}>
          {result.pantry_gap_notes.map((n, i) => (
            <p key={i} style={resultStyles.note}>
              {n}
            </p>
          ))}
          {result.substitution_suggestions.map((n, i) => (
            <p key={i} style={resultStyles.note}>
              {n}
            </p>
          ))}
          {result.confidence_notes.map((n, i) => (
            <p key={i} style={resultStyles.note}>
              {n}
            </p>
          ))}
        </section>
      )}
    </div>
  );
}

const resultStyles = {
  container: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
  },
  empty: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
  },
  section: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  sectionTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "var(--space-4)",
  },
  ideaList: {
    margin: 0,
    paddingLeft: "var(--space-5)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
  },
  ideaItem: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
  },
  notesSection: {
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: "var(--space-4)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  note: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-relaxed)",
  },
} as const;

// ── Page ──────────────────────────────────────────────────────────────────────

export function PantryPage() {
  const [ingredientsText, setIngredientsText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PantrySuggestionOut | null>(null);

  function parseIngredients(text: string): string[] {
    return text
      .split(/[\n,]/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const ingredients = parseIngredients(ingredientsText);
    if (ingredients.length === 0) return;

    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await suggestPantry(ingredients);
      setResult(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setError("AI is not available. Check LM Studio settings.");
      } else {
        setError("Pantry suggestion failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  const ingredients = parseIngredients(ingredientsText);
  const canSubmit = ingredients.length > 0 && !loading;

  return (
    <div style={pageStyles.page}>
      <header style={pageStyles.header}>
        <h1 style={pageStyles.title}>Pantry</h1>
        <p style={pageStyles.subtitle}>
          Enter what you have — get recipe ideas from the archive.
        </p>
      </header>

      <form onSubmit={handleSubmit} style={pageStyles.form}>
        <label style={pageStyles.label} htmlFor="ingredients">
          Available ingredients
          <span style={pageStyles.labelHint}>one per line or comma-separated</span>
        </label>
        <textarea
          id="ingredients"
          value={ingredientsText}
          onChange={(e) => setIngredientsText(e.target.value)}
          placeholder={"olive oil\nonion\nchicken thighs\ngarlic\ntomatoes"}
          style={pageStyles.textarea}
          rows={8}
          disabled={loading}
        />
        {ingredients.length > 0 && (
          <p style={pageStyles.count}>{ingredients.length} ingredient{ingredients.length !== 1 ? "s" : ""}</p>
        )}
        <button
          type="submit"
          style={pageStyles.submitBtn}
          disabled={!canSubmit}
        >
          {loading ? "Searching archive…" : "Suggest recipes"}
        </button>
      </form>

      {error && <p style={pageStyles.error}>{error}</p>}

      {result && <Results result={result} />}
    </div>
  );
}

const pageStyles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
    maxWidth: 840,
  },
  header: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-6)",
  },
  title: {
    fontSize: "var(--text-2xl)",
    fontWeight: 500,
  },
  subtitle: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
  },
  form: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
    maxWidth: 480,
  },
  label: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-primary)",
  },
  labelHint: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 400,
  },
  textarea: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-primary)",
    fontSize: "var(--text-sm)",
    lineHeight: "var(--leading-relaxed)",
    padding: "var(--space-3)",
    resize: "vertical" as const,
    fontFamily: "inherit",
  } as React.CSSProperties,
  count: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  submitBtn: {
    alignSelf: "flex-start" as const,
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-5)",
  } as React.CSSProperties,
  error: {
    fontSize: "var(--text-sm)",
    color: "var(--state-advisory)",
  },
} as const;

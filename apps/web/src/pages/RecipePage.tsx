import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { IngredientList } from "../components/recipe/IngredientList";
import { MetadataStrip } from "../components/recipe/MetadataStrip";
import { MetadataSuggestionPanel } from "../components/recipe/MetadataSuggestionPanel";
import { NoteBlock } from "../components/recipe/NoteBlock";
import { RewritePanel } from "../components/recipe/RewritePanel";
import { SimilarRecipesPanel } from "../components/recipe/SimilarRecipesPanel";
import { SourcePanel } from "../components/recipe/SourcePanel";
import { StepList } from "../components/recipe/StepList";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { StatusBadge } from "../components/ui/StatusBadge";
import { DEFAULT_SCALE, SCALE_OPTIONS, scaleServings } from "../lib/scaling";
import type { ScaleFactor } from "../lib/scaling";
import { useRecipe } from "../hooks/useRecipe";
import { useFavorite } from "../hooks/useFavorite";
import {
  ApiError,
  archiveRecipe,
  unarchiveRecipe,
  patchRecipe,
} from "../lib/api";
import {
  suggestMetadata,
  rewriteRecipe,
  findSimilarRecipes,
} from "../lib/recipe-ai-api";
import { queryKeys } from "../lib/queryKeys";
import type {
  MetadataSuggestionOut,
  ArchiveRewriteOut,
  SimilarRecipesOut,
} from "../lib/recipe-ai-api";

export function RecipePage() {
  const { slug } = useParams<{ slug: string }>();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { data, isLoading, isError } = useRecipe(slug ?? "");
  const [scale, setScale] = useState<ScaleFactor>(DEFAULT_SCALE);
  const favMutation = useFavorite();
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);
  const [archivePending, setArchivePending] = useState(false);

  // AI enrichment state
  const [metadata, setMetadata] = useState<MetadataSuggestionOut | null>(null);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const [metadataError, setMetadataError] = useState<string | null>(null);
  const [applyError, setApplyError] = useState<string | null>(null);
  const [appliedFields, setAppliedFields] = useState<Set<string>>(new Set());
  const [rewrite, setRewrite] = useState<ArchiveRewriteOut | null>(null);
  const [rewriteLoading, setRewriteLoading] = useState(false);
  const [rewriteError, setRewriteError] = useState<string | null>(null);
  const [similar, setSimilar] = useState<SimilarRecipesOut | null>(null);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [similarError, setSimilarError] = useState<string | null>(null);

  if (isLoading) {
    return <p style={styles.state}>Loading…</p>;
  }

  if (isError || !data) {
    return <p style={styles.stateError}>Recipe not found.</p>;
  }

  const recipe = data.data;
  const aiWorking = metadataLoading || rewriteLoading || similarLoading;

  async function handleSuggestMetadata() {
    setMetadataLoading(true);
    setMetadataError(null);
    setMetadata(null);
    setAppliedFields(new Set());
    try {
      const res = await suggestMetadata(recipe.slug);
      setMetadata(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setMetadataError("AI is not available. Check LM Studio settings.");
      } else {
        setMetadataError("Metadata suggestion failed.");
      }
    } finally {
      setMetadataLoading(false);
    }
  }

  async function handleRewrite() {
    setRewriteLoading(true);
    setRewriteError(null);
    setRewrite(null);
    try {
      const res = await rewriteRecipe(recipe.slug);
      setRewrite(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setRewriteError("AI is not available. Check LM Studio settings.");
      } else {
        setRewriteError("Archive rewrite failed.");
      }
    } finally {
      setRewriteLoading(false);
    }
  }

  async function applyField(field: string, value: unknown) {
    // Map the "class" alias to "operational_class" for the PATCH body
    const patchField = field === "class" ? "operational_class" : field;
    setApplyError(null);
    try {
      await patchRecipe(recipe.slug, { [patchField]: value });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.recipe.detail(recipe.slug),
      });
      setAppliedFields((prev) => new Set(prev).add(field));
    } catch {
      setApplyError("Failed to apply field. Please try again.");
    }
  }

  async function handleArchiveConfirm() {
    setArchivePending(true);
    try {
      if (recipe.archived) {
        await unarchiveRecipe(recipe.slug);
        await queryClient.invalidateQueries({
          queryKey: queryKeys.recipe.detail(recipe.slug),
        });
        await queryClient.invalidateQueries({
          queryKey: queryKeys.recipes.all(),
        });
      } else {
        await archiveRecipe(recipe.slug);
        // After archiving, navigate back to library since recipe is no longer visible
        await queryClient.invalidateQueries({
          queryKey: queryKeys.recipes.all(),
        });
        navigate("/library");
      }
    } catch {
      // silent
    } finally {
      setArchivePending(false);
      setShowArchiveConfirm(false);
    }
  }

  async function handleFindSimilar() {
    setSimilarLoading(true);
    setSimilarError(null);
    setSimilar(null);
    try {
      const res = await findSimilarRecipes(recipe.slug);
      setSimilar(res.data);
    } catch (err) {
      if (
        err instanceof ApiError &&
        (err.code === "ai_disabled" || err.code === "ai_unavailable")
      ) {
        setSimilarError("AI is not available. Check LM Studio settings.");
      } else {
        setSimilarError("Similar recipe search failed.");
      }
    } finally {
      setSimilarLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <ConfirmDialog
        open={showArchiveConfirm}
        title={recipe.archived ? "Unarchive recipe" : "Archive recipe"}
        message={
          recipe.archived
            ? "This recipe will be restored to the library."
            : "This recipe will be hidden from the library. You can unarchive it later."
        }
        confirmLabel={recipe.archived ? "Unarchive" : "Archive"}
        onConfirm={handleArchiveConfirm}
        onCancel={() => setShowArchiveConfirm(false)}
        destructive={!recipe.archived}
      />

      {/* Back nav */}
      <Link to="/library" style={styles.backLink} aria-label="Back to library">
        ← Library
      </Link>

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.titleRow}>
          <h1 style={styles.title}>{recipe.title}</h1>
          <div style={styles.titleMeta}>
            <StatusBadge state={recipe.verification_state} />
            <button
              type="button"
              onClick={() => {
                if (!favMutation.isPending) {
                  favMutation.mutate({
                    slug: recipe.slug,
                    isFavorite: recipe.favorite,
                  });
                }
              }}
              style={{
                ...styles.favBtn,
                color: recipe.favorite
                  ? "var(--state-favorite)"
                  : "var(--text-tertiary)",
              }}
              aria-label={
                recipe.favorite ? "Remove from favourites" : "Add to favourites"
              }
              aria-pressed={recipe.favorite}
            >
              {recipe.favorite ? "★" : "☆"}
            </button>
            <button
              type="button"
              onClick={() => setShowArchiveConfirm(true)}
              disabled={archivePending}
              style={styles.archiveBtn}
              aria-label={
                recipe.archived ? "Unarchive recipe" : "Archive recipe"
              }
            >
              {recipe.archived ? "Unarchive" : "Archive"}
            </button>
          </div>
        </div>
        {recipe.short_description && (
          <p style={styles.description}>{recipe.short_description}</p>
        )}
        <div style={styles.kitchenLink}>
          <Link
            to={`/recipe/${recipe.slug}/kitchen`}
            style={styles.kitchenAnchor}
          >
            Kitchen mode →
          </Link>
        </div>
      </header>

      {/* Metadata strip */}
      <MetadataStrip recipe={recipe} />

      {/* Two-column body */}
      <div style={styles.body}>
        <div style={styles.primary}>
          {/* Scale control — only shown when recipe has parseable servings */}
          {recipe.servings && (
            <div style={styles.scaleBar} aria-label="Scale recipe">
              <span style={styles.scaleLabel}>
                {scale !== DEFAULT_SCALE
                  ? `×${scale} — ${scaleServings(recipe.servings, scale)}`
                  : recipe.servings}
              </span>
              <div style={styles.scaleOptions}>
                {SCALE_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setScale(opt.value)}
                    style={{
                      ...styles.scaleBtn,
                      ...(scale === opt.value ? styles.scaleBtnActive : {}),
                    }}
                    aria-pressed={scale === opt.value}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}
          <IngredientList ingredients={recipe.ingredients} scale={scale} />
        </div>
        <div style={styles.secondary}>
          <StepList steps={recipe.steps} scale={scale} />
        </div>
      </div>

      {/* Notes */}
      <NoteBlock notes={recipe.notes} />

      {/* Source */}
      <SourcePanel source={recipe.source} intakeJobId={recipe.intake_job_id} />

      {/* AI Tools */}
      <section style={styles.aiSection}>
        <h2 style={styles.aiSectionTitle}>AI Tools</h2>
        <div style={styles.aiActions}>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleSuggestMetadata}
            disabled={aiWorking}
          >
            {metadataLoading ? "Suggesting…" : "Suggest metadata"}
          </button>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleRewrite}
            disabled={aiWorking}
          >
            {rewriteLoading ? "Rewriting…" : "Rewrite recipe"}
          </button>
          <button
            type="button"
            style={styles.aiBtn}
            onClick={handleFindSimilar}
            disabled={aiWorking}
          >
            {similarLoading ? "Searching…" : "Find similar"}
          </button>
        </div>
        {metadataError && <p style={styles.aiError}>{metadataError}</p>}
        {rewriteError && <p style={styles.aiError}>{rewriteError}</p>}
        {similarError && <p style={styles.aiError}>{similarError}</p>}
        {applyError && <p style={styles.aiError}>{applyError}</p>}
        {metadata && (
          <MetadataSuggestionPanel
            suggestion={metadata}
            appliedFields={appliedFields}
            onApply={applyField}
            onDismiss={() => setMetadata(null)}
          />
        )}
        {rewrite && (
          <RewritePanel rewrite={rewrite} onDismiss={() => setRewrite(null)} />
        )}
        {similar && (
          <SimilarRecipesPanel
            similar={similar}
            onDismiss={() => setSimilar(null)}
          />
        )}
      </section>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
    maxWidth: 960,
  },
  backLink: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    textDecoration: "underline",
    alignSelf: "flex-start" as const,
  },
  header: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  titleRow: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-4)",
    flexWrap: "wrap" as const,
  },
  title: {
    fontSize: "var(--text-3xl)",
    fontWeight: 500,
    letterSpacing: "var(--tracking-tight)",
    lineHeight: "var(--leading-tight)",
  },
  titleMeta: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
  },
  favBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "var(--text-lg)",
    padding: 0,
    lineHeight: 1,
    transition: "color var(--transition-fast)",
  } as React.CSSProperties,
  archiveBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    letterSpacing: "var(--tracking-wide)",
    padding: "2px var(--space-2)",
    textTransform: "uppercase" as const,
    transition: "var(--transition-fast)",
  } as React.CSSProperties,
  description: {
    fontSize: "var(--text-base)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-relaxed)",
    maxWidth: 640,
  },
  kitchenLink: {
    marginTop: "var(--space-1)",
  },
  kitchenAnchor: {
    fontSize: "var(--text-sm)",
    color: "var(--state-info)",
    textDecoration: "underline",
  },
  body: {
    display: "flex",
    gap: "var(--space-12)",
    alignItems: "flex-start",
  },
  primary: {
    minWidth: 220,
    width: 280,
    flexShrink: 0,
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  scaleBar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "var(--space-3)",
    paddingBottom: "var(--space-3)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  scaleLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontWeight: 500,
  },
  scaleOptions: {
    display: "flex",
    gap: "var(--space-1)",
  },
  scaleBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: "2px var(--space-2)",
    lineHeight: 1.4,
  } as React.CSSProperties,
  scaleBtnActive: {
    borderColor: "var(--border-primary)",
    color: "var(--text-primary)",
    background: "var(--bg-panel)",
  } as React.CSSProperties,
  secondary: {
    flex: 1,
  },
  state: {
    color: "var(--text-tertiary)",
    fontSize: "var(--text-sm)",
  },
  stateError: {
    color: "var(--state-advisory)",
    fontSize: "var(--text-sm)",
  },
  aiSection: {
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: "var(--space-6)",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  aiSectionTitle: {
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  aiActions: {
    display: "flex",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  aiBtn: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-4)",
  } as React.CSSProperties,
  aiError: {
    fontSize: "var(--text-sm)",
    color: "var(--state-advisory)",
  },
} as const;

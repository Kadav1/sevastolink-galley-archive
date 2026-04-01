import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { RecipeSummary } from "../../types/recipe";
import { useFavorite } from "../../hooks/useFavorite";
import { Badge } from "../ui/Badge";
import { StatusBadge } from "../ui/StatusBadge";

interface Props {
  recipe: RecipeSummary;
}

export function RecipeRow({ recipe }: Props) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState(false);
  const favMutation = useFavorite();

  const meta = [
    recipe.dish_role,
    recipe.primary_cuisine,
    recipe.technique_family,
  ]
    .filter(Boolean)
    .join(" · ");

  const time = recipe.total_time_minutes
    ? `${recipe.total_time_minutes} min`
    : recipe.time_class ?? null;

  const rightMeta = [recipe.servings, time].filter(Boolean) as string[];

  function handleFavClick(e: React.MouseEvent | React.KeyboardEvent) {
    e.stopPropagation();
    if (favMutation.isPending) return;
    favMutation.mutate({ slug: recipe.slug, isFavorite: recipe.favorite });
  }

  return (
    <li
      style={{
        ...styles.row,
        background: hovered ? "var(--bg-panel)" : undefined,
      }}
      onClick={() => navigate(`/recipe/${recipe.slug}`)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocus={() => setHovered(true)}
      onBlur={() => setHovered(false)}
      role="button"
      tabIndex={0}
      aria-label={`Open ${recipe.title}`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") navigate(`/recipe/${recipe.slug}`);
      }}
    >
      <div style={styles.main}>
        <div style={styles.titleRow}>
          <span style={styles.title}>{recipe.title}</span>
          <button
            type="button"
            onClick={handleFavClick}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleFavClick(e); }}
            style={{
              ...styles.favBtn,
              color: recipe.favorite ? "var(--state-favorite)" : "var(--border-primary)",
              opacity: (hovered || recipe.favorite) ? 1 : 0,
            }}
            aria-label={recipe.favorite ? "Remove from favourites" : "Add to favourites"}
            aria-pressed={recipe.favorite}
            tabIndex={-1}
          >
            ★
          </button>
        </div>
        {recipe.short_description && (
          <p style={styles.desc}>{recipe.short_description}</p>
        )}
        {meta && <p style={styles.meta}>{meta}</p>}
      </div>

      <div style={styles.right}>
        {rightMeta.map((m) => (
          <span key={m} style={styles.time}>{m}</span>
        ))}
        {recipe.complexity && (
          <Badge variant="muted">{recipe.complexity}</Badge>
        )}
        <StatusBadge state={recipe.verification_state} />
      </div>
    </li>
  );
}

const styles = {
  row: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: "var(--space-4)",
    padding: "var(--space-4) var(--space-4)",
    borderBottom: "1px solid var(--border-subtle)",
    cursor: "pointer",
    transition: "background var(--transition-fast)",
    borderRadius: "var(--radius-sm)",
    listStyle: "none",
  } as React.CSSProperties,
  main: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
    flex: 1,
    minWidth: 0,
  },
  titleRow: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-2)",
  },
  title: {
    fontSize: "var(--text-base)",
    fontWeight: 500,
    color: "var(--text-primary)",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap" as const,
  },
  favBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: 0,
    lineHeight: 1,
    flexShrink: 0,
    transition: "color var(--transition-fast), opacity var(--transition-fast)",
  } as React.CSSProperties,
  desc: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap" as const,
  },
  meta: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-normal)",
  },
  right: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "flex-end",
    gap: "var(--space-2)",
    flexShrink: 0,
  },
  time: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontFamily: "var(--font-numeric)",
  },
} as const;

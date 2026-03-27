import { buildIngredientParts, DEFAULT_SCALE } from "../../lib/scaling";
import type { ScaleFactor } from "../../lib/scaling";
import type { Ingredient } from "../../types/recipe";

interface Props {
  ingredients: Ingredient[];
  scale?: ScaleFactor;
}

export function IngredientList({ ingredients, scale = DEFAULT_SCALE }: Props) {
  if (ingredients.length === 0) {
    return <p style={styles.empty}>No ingredients recorded.</p>;
  }

  // Group by group_heading
  const groups: { heading: string | null; items: Ingredient[] }[] = [];
  for (const ing of ingredients) {
    const last = groups.at(-1);
    if (last && last.heading === ing.group_heading) {
      last.items.push(ing);
    } else {
      groups.push({ heading: ing.group_heading, items: [ing] });
    }
  }

  return (
    <section style={styles.section} aria-label="Ingredients">
      <h2 style={styles.heading}>Ingredients</h2>
      <div style={styles.content}>
        {groups.map((group, gi) => (
          <div key={gi} style={styles.group}>
            {group.heading && (
              <p style={styles.groupHeading}>{group.heading}</p>
            )}
            <ul style={styles.list}>
              {group.items.map((ing) => {
                const parts = buildIngredientParts(ing, scale);
                return (
                  <li key={ing.id} style={styles.item}>
                    {parts.displayTextOnly ? (
                      <span>{parts.quantity}</span>
                    ) : (
                      <>
                        {(parts.quantity || parts.unit) && (
                          <span
                            style={{
                              ...styles.qty,
                              ...(parts.quantityScaled ? styles.qtyScaled : {}),
                            }}
                          >
                            {[parts.quantity, parts.unit]
                              .filter(Boolean)
                              .join("\u00a0")}
                          </span>
                        )}
                        {parts.item && (
                          <span>{parts.item}</span>
                        )}
                        {parts.preparation && (
                          <span style={styles.prep}>{parts.preparation}</span>
                        )}
                      </>
                    )}
                    {ing.optional && (
                      <span style={styles.optional}>(optional)</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
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
  content: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-6)",
  },
  group: { display: "flex", flexDirection: "column" as const, gap: "var(--space-2)" },
  groupHeading: {
    fontSize: "var(--text-xs)",
    color: "var(--text-secondary)",
    fontWeight: 500,
    textTransform: "uppercase" as const,
    letterSpacing: "var(--tracking-wide)",
  },
  list: { display: "flex", flexDirection: "column" as const, gap: "var(--space-2)" },
  item: {
    display: "flex",
    flexWrap: "wrap" as const,
    alignItems: "baseline",
    gap: "0.3em",
    fontSize: "var(--text-base)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-snug)",
  },
  qty: {
    fontWeight: 500,
  } as React.CSSProperties,
  qtyScaled: {
    color: "var(--state-advisory)",
  } as React.CSSProperties,
  prep: {
    color: "var(--text-secondary)",
    fontSize: "var(--text-sm)",
  },
  optional: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
  },
  empty: { fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
} as const;

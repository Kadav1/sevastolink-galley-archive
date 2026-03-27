import { buildIngredientParts } from "../../lib/scaling";
import type { ScaleFactor } from "../../lib/scaling";
import type { Ingredient } from "../../types/recipe";

interface Props {
  ingredients: Ingredient[];
  scale: ScaleFactor;
}

export function KitchenIngredients({ ingredients, scale }: Props) {
  if (ingredients.length === 0) {
    return (
      <section style={styles.section} aria-label="Ingredients">
        <h2 style={styles.sectionLabel}>Ingredients</h2>
        <p style={styles.empty}>No ingredients recorded.</p>
      </section>
    );
  }

  // Group by heading
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
      <h2 style={styles.sectionLabel}>Ingredients</h2>
      <div style={styles.groups}>
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
                      <span style={styles.itemName}>{parts.quantity}</span>
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
                          <span style={styles.itemName}>{parts.item}</span>
                        )}
                        {parts.preparation && (
                          <span style={styles.prep}>{parts.preparation}</span>
                        )}
                      </>
                    )}
                    {ing.optional && (
                      <span style={styles.optional}>optional</span>
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
  groups: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-8)",
  },
  group: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  groupHeading: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    fontWeight: 500,
    textTransform: "uppercase" as const,
    letterSpacing: "var(--tracking-wide)",
    marginBottom: "var(--space-1)",
  },
  list: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
    paddingLeft: 0,
    listStyle: "none",
  },
  item: {
    display: "flex",
    flexWrap: "wrap" as const,
    alignItems: "baseline",
    gap: "0.4em",
    fontSize: "var(--text-md)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-snug)",
  },
  qty: {
    fontWeight: 500,
    color: "var(--text-primary)",
    minWidth: "fit-content",
  } as React.CSSProperties,
  qtyScaled: {
    color: "var(--state-advisory)",
  } as React.CSSProperties,
  itemName: {
    color: "var(--text-primary)",
  },
  prep: {
    color: "var(--text-secondary)",
    fontSize: "var(--text-base)",
  },
  optional: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontStyle: "italic",
  },
  empty: {
    fontSize: "var(--text-base)",
    color: "var(--text-tertiary)",
  },
} as const;

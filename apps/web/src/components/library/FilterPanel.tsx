import {
  DISH_ROLE_FILTER_OPTIONS,
  CUISINE_FILTER_OPTIONS,
  TECHNIQUE_FILTER_OPTIONS,
  COMPLEXITY_OPTIONS,
  TIME_CLASS_OPTIONS,
  INGREDIENT_FAMILY_FILTER_OPTIONS,
} from "@galley/shared-taxonomy";
import type { VerificationState } from "../../types/recipe";

type FilterKey = "verification_state" | "dish_role" | "primary_cuisine" | "technique_family" | "complexity" | "time_class" | "ingredient_family" | "favorite";

export interface ActiveFilters {
  verification_state?: VerificationState;
  dish_role?: string;
  primary_cuisine?: string;
  technique_family?: string;
  complexity?: string;
  time_class?: string;
  ingredient_family?: string;
  favorite?: boolean;
}

interface Props {
  filters: ActiveFilters;
  onChange: (filters: ActiveFilters) => void;
}

const VERIFICATION_OPTIONS: VerificationState[] = ["Verified", "Unverified", "Draft", "Archived"];

interface FilterGroupProps {
  label: string;
  options: readonly string[];
  value?: string;
  onSelect: (v: string | undefined) => void;
}

function FilterGroup({ label, options, value, onSelect }: FilterGroupProps) {
  return (
    <div style={styles.group}>
      <p style={styles.groupLabel}>{label}</p>
      <div style={styles.chips}>
        {options.map((opt) => (
          <button
            key={opt}
            onClick={() => onSelect(value === opt ? undefined : opt)}
            style={{
              ...styles.chip,
              ...(value === opt ? styles.chipActive : {}),
            }}
            type="button"
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}

export function FilterPanel({ filters, onChange }: Props) {
  const hasActive =
    Object.values(filters).some((v) => v !== undefined && v !== false);

  function set(key: FilterKey, value: string | boolean | undefined) {
    onChange({ ...filters, [key]: value });
  }

  function clearAll() {
    onChange({});
  }

  return (
    <aside style={styles.panel} aria-label="Filter recipes">
      <div style={styles.header}>
        <span style={styles.panelLabel}>Filters</span>
        {hasActive && (
          <button onClick={clearAll} style={styles.clearBtn} type="button">
            Clear all
          </button>
        )}
      </div>

      {/* Favorite quick toggle */}
      <div style={styles.group}>
        <button
          onClick={() => set("favorite", filters.favorite ? undefined : true)}
          style={{
            ...styles.chip,
            ...(filters.favorite ? styles.chipActive : {}),
          }}
          type="button"
        >
          ★ Favourites
        </button>
      </div>

      <FilterGroup
        label="State"
        options={VERIFICATION_OPTIONS}
        value={filters.verification_state}
        onSelect={(v) => set("verification_state", v as VerificationState | undefined)}
      />
      <FilterGroup
        label="Dish Role"
        options={DISH_ROLE_FILTER_OPTIONS}
        value={filters.dish_role}
        onSelect={(v) => set("dish_role", v)}
      />
      <FilterGroup
        label="Cuisine"
        options={CUISINE_FILTER_OPTIONS}
        value={filters.primary_cuisine}
        onSelect={(v) => set("primary_cuisine", v)}
      />
      <FilterGroup
        label="Technique"
        options={TECHNIQUE_FILTER_OPTIONS}
        value={filters.technique_family}
        onSelect={(v) => set("technique_family", v)}
      />
      <FilterGroup
        label="Complexity"
        options={COMPLEXITY_OPTIONS}
        value={filters.complexity}
        onSelect={(v) => set("complexity", v)}
      />
      <FilterGroup
        label="Time"
        options={TIME_CLASS_OPTIONS}
        value={filters.time_class}
        onSelect={(v) => set("time_class", v)}
      />
      <FilterGroup
        label="Ingredient"
        options={INGREDIENT_FAMILY_FILTER_OPTIONS}
        value={filters.ingredient_family}
        onSelect={(v) => set("ingredient_family", v)}
      />
    </aside>
  );
}

const styles = {
  panel: {
    width: 200,
    minWidth: 200,
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-6)",
    paddingRight: "var(--space-6)",
    borderRight: "1px solid var(--border-subtle)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  panelLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    fontWeight: 600,
  },
  clearBtn: {
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: 0,
    textDecoration: "underline",
  },
  group: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
  },
  groupLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-secondary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  chips: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "var(--space-1)",
  },
  chip: {
    padding: "3px var(--space-2)",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--border-subtle)",
    background: "var(--bg-panel)",
    color: "var(--text-secondary)",
    fontSize: "var(--text-xs)",
    cursor: "pointer",
    transition: "background var(--transition-fast), color var(--transition-fast)",
    lineHeight: 1.4,
  } as React.CSSProperties,
  chipActive: {
    background: "var(--bg-overlay)",
    border: "1px solid var(--border-primary)",
    color: "var(--text-primary)",
  } as React.CSSProperties,
} as const;

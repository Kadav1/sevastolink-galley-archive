import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FilterPanel, type ActiveFilters } from "../components/library/FilterPanel";
import { RecipeRow } from "../components/library/RecipeRow";
import { SearchBar } from "../components/library/SearchBar";
import { useRecipes } from "../hooks/useRecipes";
import type { RecipeListParams, VerificationState } from "../types/recipe";

const PAGE_LIMIT = 50;

function buildParams(q: string, filters: ActiveFilters, offset: number): RecipeListParams {
  const params: RecipeListParams = { limit: PAGE_LIMIT, offset };
  if (q) params.q = q;
  if (filters.verification_state) params.verification_state = filters.verification_state;
  if (filters.dish_role) params.dish_role = filters.dish_role;
  if (filters.primary_cuisine) params.primary_cuisine = filters.primary_cuisine;
  if (filters.technique_family) params.technique_family = filters.technique_family;
  if (filters.complexity) params.complexity = filters.complexity;
  if (filters.time_class) params.time_class = filters.time_class;
  if (filters.favorite) params.favorite = true;
  return params;
}

function filtersFromSearch(params: URLSearchParams): ActiveFilters {
  return {
    verification_state: (params.get("verification_state") ?? undefined) as VerificationState | undefined,
    dish_role: params.get("dish_role") ?? undefined,
    primary_cuisine: params.get("primary_cuisine") ?? undefined,
    technique_family: params.get("technique_family") ?? undefined,
    complexity: params.get("complexity") ?? undefined,
    time_class: params.get("time_class") ?? undefined,
    favorite: params.get("favorite") === "true" ? true : undefined,
  };
}

export function LibraryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [q, setQ] = useState(searchParams.get("q") ?? "");
  const filters = filtersFromSearch(searchParams);
  const offset = Math.max(0, parseInt(searchParams.get("offset") ?? "0", 10) || 0);

  const queryParams = buildParams(q, filters, offset);
  const { data, isLoading, isError } = useRecipes(queryParams);

  const handleSearch = useCallback((value: string) => {
    setQ(value);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) next.set("q", value);
      else next.delete("q");
      next.delete("offset"); // reset page on new search
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const handleFilters = useCallback((next: ActiveFilters) => {
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      const keys: (keyof ActiveFilters)[] = [
        "verification_state", "dish_role", "primary_cuisine", "technique_family",
        "complexity", "time_class", "favorite",
      ];
      for (const key of keys) {
        const val = next[key];
        if (val !== undefined && val !== false) p.set(key, String(val));
        else p.delete(key);
      }
      p.delete("offset"); // reset page on filter change
      return p;
    }, { replace: true });
  }, [setSearchParams]);

  const setOffset = useCallback((next: number) => {
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      if (next > 0) p.set("offset", String(next));
      else p.delete("offset");
      return p;
    }, { replace: true });
  }, [setSearchParams]);

  const recipes = data?.data ?? [];
  const total = data?.meta.total ?? 0;
  const hasPrev = offset > 0;
  const hasNext = offset + PAGE_LIMIT < total;
  const page = Math.floor(offset / PAGE_LIMIT) + 1;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_LIMIT));

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Library</h1>
        {!isLoading && (
          <p style={styles.count}>
            {total} {total === 1 ? "recipe" : "recipes"}
          </p>
        )}
      </header>

      <div style={styles.searchRow}>
        <SearchBar value={q} onChange={handleSearch} />
      </div>

      <div style={styles.body}>
        <FilterPanel filters={filters} onChange={handleFilters} />

        <div style={styles.listColumn}>
          <div style={styles.list} role="list" aria-label="Recipe list">
            {isLoading && (
              <p style={styles.state}>Loading…</p>
            )}
            {isError && (
              <p style={styles.stateError}>Failed to load recipes.</p>
            )}
            {!isLoading && !isError && recipes.length === 0 && (
              <p style={styles.state}>
                {q || Object.values(filters).some(Boolean)
                  ? "No recipes match these filters."
                  : "No recipes yet. Use Intake to add the first one."}
              </p>
            )}
            {recipes.map((recipe) => (
              <RecipeRow key={recipe.id} recipe={recipe} />
            ))}
          </div>

          {totalPages > 1 && (
            <div style={styles.pagination} aria-label="Pagination">
              <button
                type="button"
                style={{ ...styles.pageBtn, ...(hasPrev ? {} : styles.pageBtnDisabled) }}
                onClick={() => setOffset(Math.max(0, offset - PAGE_LIMIT))}
                disabled={!hasPrev}
                aria-label="Previous page"
              >
                ← Prev
              </button>
              <span style={styles.pageIndicator}>
                {page} / {totalPages}
              </span>
              <button
                type="button"
                style={{ ...styles.pageBtn, ...(hasNext ? {} : styles.pageBtnDisabled) }}
                onClick={() => setOffset(offset + PAGE_LIMIT)}
                disabled={!hasNext}
                aria-label="Next page"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-6)",
    height: "100%",
  },
  header: {
    display: "flex",
    alignItems: "baseline",
    gap: "var(--space-4)",
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-6)",
  },
  title: {
    fontSize: "var(--text-2xl)",
    fontWeight: 500,
    letterSpacing: "var(--tracking-tight)",
  },
  count: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
  },
  searchRow: {
    width: "100%",
  },
  body: {
    display: "flex",
    gap: "var(--space-8)",
    alignItems: "flex-start",
    flex: 1,
  },
  listColumn: {
    flex: 1,
    display: "flex",
    flexDirection: "column" as const,
    gap: 0,
  },
  list: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 0,
  },
  pagination: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-4)",
    paddingTop: "var(--space-6)",
    borderTop: "1px solid var(--border-subtle)",
    marginTop: "var(--space-4)",
  },
  pageBtn: {
    background: "none",
    border: "1px solid var(--border-primary)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-1) var(--space-3)",
    transition: "var(--transition-fast)",
  } as React.CSSProperties,
  pageBtnDisabled: {
    borderColor: "var(--border-subtle)",
    color: "var(--text-tertiary)",
    cursor: "default",
    opacity: 0.5,
  } as React.CSSProperties,
  pageIndicator: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    fontVariantNumeric: "tabular-nums",
  } as React.CSSProperties,
  state: {
    color: "var(--text-tertiary)",
    fontSize: "var(--text-sm)",
  },
  stateError: {
    color: "var(--state-advisory)",
    fontSize: "var(--text-sm)",
  },
} as const;

import { useEffect, useRef, useState } from "react";

interface Props {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = "Search archive…" }: Props) {
  const [local, setLocal] = useState(value);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync external value resets (e.g., clear all filters)
  useEffect(() => {
    setLocal(value);
  }, [value]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = e.target.value;
    setLocal(v);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => onChange(v), 300);
  }

  function handleClear() {
    setLocal("");
    if (timer.current) clearTimeout(timer.current);
    onChange("");
  }

  return (
    <div style={styles.wrapper} role="search">
      <label htmlFor="global-search" style={styles.label}>
        Search
      </label>
      <div style={styles.inputWrapper}>
        <input
          id="global-search"
          type="search"
          value={local}
          onChange={handleChange}
          placeholder={placeholder}
          style={styles.input}
          autoComplete="off"
        />
        {local && (
          <button
            onClick={handleClear}
            style={styles.clear}
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-1)",
  },
  label: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wide)",
    textTransform: "uppercase" as const,
  },
  inputWrapper: {
    position: "relative" as const,
    display: "flex",
    alignItems: "center",
  },
  input: {
    width: "100%",
    fontSize: "var(--text-base)",
    background: "var(--bg-field)",
    border: "1px solid var(--border-primary)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-primary)",
    padding: "var(--space-3) var(--space-4)",
    paddingRight: "var(--space-10)",
    outline: "none",
  } as React.CSSProperties,
  clear: {
    position: "absolute" as const,
    right: "var(--space-3)",
    background: "none",
    border: "none",
    color: "var(--text-tertiary)",
    cursor: "pointer",
    fontSize: "var(--text-xs)",
    padding: "var(--space-1)",
    lineHeight: 1,
  },
} as const;

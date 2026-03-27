export function SettingsPage() {
  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Settings</h1>
        <p style={styles.subtitle}>Archive configuration and preferences</p>
      </header>
      <p style={styles.placeholder}>Settings — not yet implemented.</p>
    </div>
  );
}

const styles = {
  page: { display: "flex", flexDirection: "column" as const, gap: "var(--space-8)" },
  header: { borderBottom: "1px solid var(--border-subtle)", paddingBottom: "var(--space-6)" },
  title: { fontSize: "var(--text-2xl)", fontWeight: 500 },
  subtitle: { marginTop: "var(--space-1)", fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
  placeholder: { color: "var(--text-tertiary)", fontSize: "var(--text-sm)" },
} as const;

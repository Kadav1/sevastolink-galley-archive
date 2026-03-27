import { useNavigate } from "react-router-dom";

interface PathCardProps {
  title: string;
  description: string;
  detail: string;
  onClick: () => void;
}

function PathCard({ title, description, detail, onClick }: PathCardProps) {
  return (
    <button onClick={onClick} style={styles.card} type="button">
      <div style={styles.cardTitle}>{title}</div>
      <p style={styles.cardDesc}>{description}</p>
      <p style={styles.cardDetail}>{detail}</p>
    </button>
  );
}

export function IntakePage() {
  const navigate = useNavigate();

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Intake</h1>
        <p style={styles.subtitle}>
          Bring recipe material into the archive with source preserved and trust stated.
        </p>
      </header>

      <div style={styles.paths}>
        <PathCard
          title="Manual Entry"
          description="Compose a recipe directly."
          detail="Best for household standards, personal recipes, and transcribed notes. Saves straight into the archive."
          onClick={() => navigate("/intake/manual")}
        />
        <PathCard
          title="Paste Text"
          description="Paste raw text and structure it."
          detail="Best for copied website text, message threads, or informal writeups. Raw source is preserved automatically."
          onClick={() => navigate("/intake/paste")}
        />
      </div>

      <div style={styles.deferred}>
        <p style={styles.deferredLabel}>Coming later</p>
        <div style={styles.deferredItems}>
          <span style={styles.deferredItem}>URL import</span>
          <span style={styles.deferredItem}>File / image intake</span>
          <span style={styles.deferredItem}>AI-assisted structuring</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-10)",
    maxWidth: 760,
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
    letterSpacing: "var(--tracking-tight)",
  },
  subtitle: {
    fontSize: "var(--text-sm)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-relaxed)",
    maxWidth: 480,
  },
  paths: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-4)",
  },
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    padding: "var(--space-6)",
    textAlign: "left" as const,
    cursor: "pointer",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
    transition: "border-color var(--transition-fast)",
  } as React.CSSProperties,
  cardTitle: {
    fontSize: "var(--text-base)",
    fontWeight: 600,
    color: "var(--text-primary)",
    letterSpacing: "var(--tracking-tight)",
  },
  cardDesc: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    fontWeight: 500,
  },
  cardDetail: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    lineHeight: "var(--leading-relaxed)",
  },
  deferred: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-3)",
  },
  deferredLabel: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    fontWeight: 600,
  },
  deferredItems: {
    display: "flex",
    gap: "var(--space-3)",
    flexWrap: "wrap" as const,
  },
  deferredItem: {
    fontSize: "var(--text-xs)",
    color: "var(--text-tertiary)",
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    padding: "3px var(--space-3)",
  },
} as const;

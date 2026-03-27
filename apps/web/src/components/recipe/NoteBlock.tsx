import type { Note, NoteType } from "../../types/recipe";

interface Props {
  notes: Note[];
}

const NOTE_LABELS: Record<NoteType, string> = {
  recipe: "Recipe Notes",
  service: "Service",
  storage: "Storage",
  substitution: "Substitutions",
  source: "Source Notes",
};

const NOTE_ORDER: NoteType[] = ["recipe", "service", "storage", "substitution", "source"];

export function NoteBlock({ notes }: Props) {
  if (notes.length === 0) return null;

  const byType = new Map<NoteType, Note>();
  for (const note of notes) {
    byType.set(note.note_type as NoteType, note);
  }

  const ordered = NOTE_ORDER.filter((t) => byType.has(t));
  if (ordered.length === 0) return null;

  return (
    <section style={styles.section} aria-label="Notes">
      <h2 style={styles.heading}>Notes</h2>
      <div style={styles.blocks}>
        {ordered.map((type) => {
          const note = byType.get(type)!;
          return (
            <div key={type} style={styles.block}>
              <p style={styles.label}>{NOTE_LABELS[type]}</p>
              <p style={styles.content}>{note.content}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

const styles = {
  section: { display: "flex", flexDirection: "column" as const, gap: "var(--space-4)" },
  heading: {
    fontSize: "var(--text-sm)",
    fontWeight: 600,
    color: "var(--text-tertiary)",
    letterSpacing: "var(--tracking-wider)",
    textTransform: "uppercase" as const,
    borderBottom: "1px solid var(--border-subtle)",
    paddingBottom: "var(--space-3)",
  },
  blocks: { display: "flex", flexDirection: "column" as const, gap: "var(--space-6)" },
  block: { display: "flex", flexDirection: "column" as const, gap: "var(--space-2)" },
  label: {
    fontSize: "var(--text-xs)",
    color: "var(--text-secondary)",
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "var(--tracking-wide)",
  },
  content: {
    fontSize: "var(--text-base)",
    color: "var(--text-primary)",
    lineHeight: "var(--leading-relaxed)",
  },
} as const;

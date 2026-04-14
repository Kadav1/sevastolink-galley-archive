import type { ArchiveRewriteOut } from "../../lib/recipe-ai-api";
import { panelStyles } from "./aiPanelStyles";

export interface RewritePanelProps {
  rewrite: ArchiveRewriteOut;
  onDismiss: () => void;
}

export function RewritePanel({ rewrite, onDismiss }: RewritePanelProps) {
  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Archive rewrite suggestion</span>
        <button
          type="button"
          onClick={onDismiss}
          style={panelStyles.dismissBtn}
        >
          Dismiss
        </button>
      </div>

      <p style={panelStyles.rewriteNote}>
        Read-only preview — does not modify the stored recipe.
      </p>

      {rewrite.title && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Title</span>
          <p style={panelStyles.rewriteText}>{rewrite.title}</p>
        </div>
      )}

      {rewrite.short_description && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Description</span>
          <p style={panelStyles.rewriteText}>{rewrite.short_description}</p>
        </div>
      )}

      {rewrite.ingredients.length > 0 && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Ingredients</span>
          <ul style={panelStyles.rewriteList}>
            {rewrite.ingredients.map((ing, i) => {
              const parts = [ing.amount, ing.unit, ing.item]
                .filter(Boolean)
                .join(" ");
              const note = ing.note ? ` — ${ing.note}` : "";
              return (
                <li key={i} style={panelStyles.rewriteListItem}>
                  {parts}
                  {note}
                  {ing.optional && " (optional)"}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {rewrite.steps.length > 0 && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Steps</span>
          <ol style={panelStyles.rewriteList}>
            {rewrite.steps.map((step) => (
              <li key={step.step_number} style={panelStyles.rewriteListItem}>
                {step.instruction}
                {step.time_note && (
                  <span style={panelStyles.rewriteMeta}>
                    {" "}
                    [{step.time_note}]
                  </span>
                )}
                {step.heat_note && (
                  <span style={panelStyles.rewriteMeta}>
                    {" "}
                    [{step.heat_note}]
                  </span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      {rewrite.recipe_notes && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Notes</span>
          <p style={panelStyles.rewriteText}>{rewrite.recipe_notes}</p>
        </div>
      )}

      {rewrite.service_notes && (
        <div style={panelStyles.rewriteSection}>
          <span style={panelStyles.rewriteLabel}>Service notes</span>
          <p style={panelStyles.rewriteText}>{rewrite.service_notes}</p>
        </div>
      )}

      {(rewrite.rewrite_notes.length > 0 ||
        rewrite.uncertainty_notes.length > 0) && (
        <div style={panelStyles.notes}>
          {rewrite.rewrite_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>
              {n}
            </p>
          ))}
          {rewrite.uncertainty_notes.map((n, i) => (
            <p
              key={i}
              style={{
                ...panelStyles.noteItem,
                color: "var(--state-advisory)",
              }}
            >
              ⚠ {n}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

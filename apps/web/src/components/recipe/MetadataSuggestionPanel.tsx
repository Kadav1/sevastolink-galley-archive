import type { MetadataSuggestionOut } from "../../lib/recipe-ai-api";
import { panelStyles } from "./aiPanelStyles";

const SCALAR_FIELDS: Array<{
  key: keyof MetadataSuggestionOut;
  label: string;
}> = [
  { key: "short_description", label: "Short description" },
  { key: "dish_role", label: "Dish role" },
  { key: "primary_cuisine", label: "Primary cuisine" },
  { key: "technique_family", label: "Technique family" },
  { key: "complexity", label: "Complexity" },
  { key: "time_class", label: "Time class" },
  { key: "service_format", label: "Service format" },
  { key: "season", label: "Season" },
  { key: "sector", label: "Sector" },
  { key: "class", label: "Operational class" },
  { key: "heat_window", label: "Heat window" },
];

const ARRAY_FIELDS: Array<{ key: keyof MetadataSuggestionOut; label: string }> =
  [
    { key: "secondary_cuisines", label: "Secondary cuisines" },
    { key: "ingredient_families", label: "Ingredient families" },
    { key: "mood_tags", label: "Mood tags" },
    { key: "storage_profile", label: "Storage profile" },
    { key: "dietary_flags", label: "Dietary flags" },
    { key: "provision_tags", label: "Provision tags" },
  ];

export interface MetadataSuggestionPanelProps {
  suggestion: MetadataSuggestionOut;
  appliedFields: Set<string>;
  onApply: (field: string, value: unknown) => void;
  onDismiss: () => void;
}

export function MetadataSuggestionPanel({
  suggestion,
  appliedFields,
  onApply,
  onDismiss,
}: MetadataSuggestionPanelProps) {
  const hasNotes =
    suggestion.confidence_notes.length > 0 ||
    suggestion.uncertainty_notes.length > 0;

  return (
    <div style={panelStyles.panel}>
      <div style={panelStyles.panelHeader}>
        <span style={panelStyles.panelTitle}>Metadata suggestions</span>
        <button
          type="button"
          onClick={onDismiss}
          style={panelStyles.dismissBtn}
        >
          Dismiss
        </button>
      </div>

      <div style={panelStyles.fieldList}>
        {SCALAR_FIELDS.map(({ key, label }) => {
          const val = suggestion[key] as string | null;
          if (!val) return null;
          const applied = appliedFields.has(key);
          return (
            <div key={key} style={panelStyles.fieldRow}>
              <span style={panelStyles.fieldLabel}>{label}</span>
              <span style={panelStyles.fieldValue}>{val}</span>
              <button
                type="button"
                style={
                  applied ? panelStyles.applyBtnApplied : panelStyles.applyBtn
                }
                disabled={applied}
                onClick={() => onApply(key, val)}
              >
                {applied ? "Applied" : "Apply"}
              </button>
            </div>
          );
        })}

        {ARRAY_FIELDS.map(({ key, label }) => {
          const val = suggestion[key] as string[];
          if (!val || val.length === 0) return null;
          const applied = appliedFields.has(key);
          return (
            <div key={key} style={panelStyles.fieldRow}>
              <span style={panelStyles.fieldLabel}>{label}</span>
              <span style={panelStyles.fieldValue}>{val.join(", ")}</span>
              <button
                type="button"
                style={
                  applied ? panelStyles.applyBtnApplied : panelStyles.applyBtn
                }
                disabled={applied}
                onClick={() => onApply(key, val)}
              >
                {applied ? "Applied" : "Apply"}
              </button>
            </div>
          );
        })}
      </div>

      {hasNotes && (
        <div style={panelStyles.notes}>
          {suggestion.confidence_notes.map((n, i) => (
            <p key={i} style={panelStyles.noteItem}>
              {n}
            </p>
          ))}
          {suggestion.uncertainty_notes.map((n, i) => (
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

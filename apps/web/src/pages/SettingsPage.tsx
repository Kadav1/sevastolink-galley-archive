import { useState } from "react";
import { useSettings, useUpdateSettings } from "../hooks/useSettings";
import type { AiHealth, Settings } from "../lib/settings-api";
import { getAiHealth } from "../lib/settings-api";

// ── Sub-components ─────────────────────────────────────────────────────────────

function SettingRow({
  label,
  description,
  children,
}: {
  label: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div style={rowStyles.row}>
      <div style={rowStyles.labels}>
        <span style={rowStyles.label}>{label}</span>
        <span style={rowStyles.description}>{description}</span>
      </div>
      <div style={rowStyles.control}>{children}</div>
    </div>
  );
}

const rowStyles = {
  row: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "var(--space-6)",
    paddingBlock: "var(--space-5)",
    borderBottom: "1px solid var(--border-subtle)",
  },
  labels: { display: "flex", flexDirection: "column" as const, gap: "var(--space-1)" },
  label: { fontSize: "var(--text-sm)", fontWeight: 500, color: "var(--text-primary)" },
  description: { fontSize: "var(--text-xs)", color: "var(--text-tertiary)" },
  control: { flexShrink: 0 },
} as const;

// ── Select helper ──────────────────────────────────────────────────────────────

function Select<T extends string>({
  value,
  onChange,
  options,
  disabled,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
  disabled?: boolean;
}) {
  return (
    <select
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value as T)}
      style={selectStyles.select}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

const selectStyles = {
  select: {
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-3)",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--border-subtle)",
    background: "var(--surface-base)",
    color: "var(--text-primary)",
    cursor: "pointer",
    minWidth: 180,
  },
} as const;

// ── Page ───────────────────────────────────────────────────────────────────────

const SORT_OPTIONS: { value: Settings["library_default_sort"]; label: string }[] = [
  { value: "updated_at_desc", label: "Recently updated" },
  { value: "created_at_desc", label: "Recently added" },
  { value: "title_asc", label: "Title A → Z" },
  { value: "title_desc", label: "Title Z → A" },
];

const VERIFICATION_OPTIONS: {
  value: Settings["default_verification_state"];
  label: string;
}[] = [
  { value: "Draft", label: "Draft" },
  { value: "Unverified", label: "Unverified" },
];

export function SettingsPage() {
  const { data: settings, isLoading, isError } = useSettings();
  const { mutate: saveSettings, isPending: isSaving } = useUpdateSettings();
  const [aiHealth, setAiHealth] = useState<AiHealth | null>(null);
  const [checkingAi, setCheckingAi] = useState(false);

  async function handleCheckAi() {
    setCheckingAi(true);
    setAiHealth(null);
    try {
      const res = await getAiHealth();
      setAiHealth(res.data);
    } catch {
      setAiHealth({ ai_enabled: true, reachable: false, model: null, error: "Network error — API unreachable" });
    } finally {
      setCheckingAi(false);
    }
  }

  if (isLoading) {
    return (
      <div style={pageStyles.page}>
        <header style={pageStyles.header}>
          <h1 style={pageStyles.title}>Settings</h1>
        </header>
        <p style={pageStyles.notice}>Loading…</p>
      </div>
    );
  }

  if (isError || !settings) {
    return (
      <div style={pageStyles.page}>
        <header style={pageStyles.header}>
          <h1 style={pageStyles.title}>Settings</h1>
        </header>
        <p style={pageStyles.error}>Could not load settings. Is the API running?</p>
      </div>
    );
  }

  const disabled = isSaving;

  return (
    <div style={pageStyles.page}>
      <header style={pageStyles.header}>
        <h1 style={pageStyles.title}>Settings</h1>
        <p style={pageStyles.subtitle}>Archive configuration and preferences</p>
      </header>

      {/* ── Library ──────────────────────────────────────────────────────── */}
      <section style={pageStyles.section}>
        <h2 style={pageStyles.sectionTitle}>Library</h2>

        <SettingRow
          label="Default sort order"
          description="How the recipe library is sorted when you open it."
        >
          <Select
            value={settings.library_default_sort}
            options={SORT_OPTIONS}
            disabled={disabled}
            onChange={(v) => saveSettings({ library_default_sort: v })}
          />
        </SettingRow>

        <SettingRow
          label="Default verification state"
          description="State applied to new recipes when added manually."
        >
          <Select
            value={settings.default_verification_state}
            options={VERIFICATION_OPTIONS}
            disabled={disabled}
            onChange={(v) => saveSettings({ default_verification_state: v })}
          />
        </SettingRow>
      </section>

      {/* ── AI ───────────────────────────────────────────────────────────── */}
      <section style={pageStyles.section}>
        <h2 style={pageStyles.sectionTitle}>AI assistance</h2>

        <SettingRow
          label="AI features"
          description="Controlled by LM_STUDIO_ENABLED in your server configuration."
        >
          <span style={settings.ai_enabled ? pageStyles.badgeOn : pageStyles.badgeOff}>
            {settings.ai_enabled ? "Enabled" : "Disabled"}
          </span>
        </SettingRow>

        {settings.ai_enabled && (
          <SettingRow
            label="LM Studio connection"
            description="Test whether the configured LM Studio instance is reachable."
          >
            <div style={pageStyles.aiCheckArea}>
              <button
                type="button"
                style={pageStyles.checkBtn}
                onClick={handleCheckAi}
                disabled={checkingAi}
              >
                {checkingAi ? "Checking…" : "Check connection"}
              </button>
              {aiHealth !== null && (
                <span
                  style={
                    aiHealth.reachable
                      ? pageStyles.aiStatusOk
                      : pageStyles.aiStatusFail
                  }
                >
                  {aiHealth.reachable
                    ? `Connected${aiHealth.model ? ` — ${aiHealth.model}` : ""}`
                    : `Unreachable${aiHealth.error ? `: ${aiHealth.error}` : ""}`}
                </span>
              )}
            </div>
          </SettingRow>
        )}
      </section>

      {isSaving && <p style={pageStyles.notice}>Saving…</p>}
    </div>
  );
}

const pageStyles = {
  page: { display: "flex", flexDirection: "column" as const, gap: "var(--space-8)" },
  header: { borderBottom: "1px solid var(--border-subtle)", paddingBottom: "var(--space-6)" },
  title: { fontSize: "var(--text-2xl)", fontWeight: 500 },
  subtitle: { marginTop: "var(--space-1)", fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
  section: { display: "flex", flexDirection: "column" as const },
  sectionTitle: {
    fontSize: "var(--text-base)",
    fontWeight: 500,
    marginBottom: "var(--space-2)",
    color: "var(--text-secondary)",
  },
  notice: { fontSize: "var(--text-sm)", color: "var(--text-tertiary)" },
  error: { fontSize: "var(--text-sm)", color: "var(--color-error, #c0392b)" },
  badgeOn: {
    fontSize: "var(--text-xs)",
    padding: "var(--space-1) var(--space-3)",
    borderRadius: "var(--radius-sm)",
    background: "var(--color-success-subtle, #d4edda)",
    color: "var(--color-success, #155724)",
  },
  badgeOff: {
    fontSize: "var(--text-xs)",
    padding: "var(--space-1) var(--space-3)",
    borderRadius: "var(--radius-sm)",
    background: "var(--surface-muted, #f0f0f0)",
    color: "var(--text-tertiary)",
  },
  aiCheckArea: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-2)",
    alignItems: "flex-end",
  },
  checkBtn: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-4)",
  } as React.CSSProperties,
  aiStatusOk: {
    fontSize: "var(--text-xs)",
    color: "var(--state-verified)",
  },
  aiStatusFail: {
    fontSize: "var(--text-xs)",
    color: "var(--state-advisory)",
    maxWidth: 280,
  },
} as const;

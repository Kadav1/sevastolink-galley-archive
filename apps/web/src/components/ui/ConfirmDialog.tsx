/**
 * ConfirmDialog — modal confirmation for destructive or irreversible actions.
 *
 * Usage:
 *   <ConfirmDialog
 *     open={showConfirm}
 *     title="Archive recipe"
 *     message="This recipe will be hidden from the library. You can unarchive it later."
 *     confirmLabel="Archive"
 *     onConfirm={handleArchive}
 *     onCancel={() => setShowConfirm(false)}
 *   />
 */

import type { CSSProperties } from "react";
import { useEffect } from "react";

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  /** When true, the confirm button renders in a muted state (default = advisory). */
  destructive?: boolean;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  destructive = true,
}: Props) {
  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onCancel();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      style={styles.backdrop}
      onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}
      aria-modal="true"
      role="dialog"
      aria-labelledby="confirm-dialog-title"
    >
      <div style={styles.dialog}>
        <h2 id="confirm-dialog-title" style={styles.title}>{title}</h2>
        <p style={styles.message}>{message}</p>
        <div style={styles.actions}>
          <button type="button" style={styles.cancelBtn} onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            type="button"
            style={{ ...styles.confirmBtn, ...(destructive ? styles.confirmDestructive : styles.confirmDefault) }}
            onClick={onConfirm}
            autoFocus
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  backdrop: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 50,
    padding: "var(--space-4)",
  },
  dialog: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-md)",
    padding: "var(--space-8)",
    maxWidth: 400,
    width: "100%",
    display: "flex",
    flexDirection: "column" as const,
    gap: "var(--space-4)",
  },
  title: {
    fontSize: "var(--text-base)",
    fontWeight: 500,
    color: "var(--text-primary)",
    margin: 0,
  },
  message: {
    fontSize: "var(--text-sm)",
    color: "var(--text-secondary)",
    lineHeight: "var(--leading-normal)",
    margin: 0,
  },
  actions: {
    display: "flex",
    gap: "var(--space-3)",
    justifyContent: "flex-end",
    paddingTop: "var(--space-2)",
  },
  cancelBtn: {
    background: "none",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    padding: "var(--space-2) var(--space-4)",
    transition: "var(--transition-fast)",
  } as CSSProperties,
  confirmBtn: {
    borderRadius: "var(--radius-sm)",
    cursor: "pointer",
    fontSize: "var(--text-sm)",
    fontWeight: 500,
    padding: "var(--space-2) var(--space-4)",
    border: "1px solid transparent",
    transition: "var(--transition-fast)",
  } as CSSProperties,
  confirmDestructive: {
    background: "var(--state-advisory)",
    color: "var(--bg-base)",
    borderColor: "var(--state-advisory)",
  } as CSSProperties,
  confirmDefault: {
    background: "var(--bg-overlay)",
    color: "var(--text-primary)",
    borderColor: "var(--border-primary)",
  } as CSSProperties,
} as const;

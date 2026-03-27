/**
 * Sevastolink Galley Archive — UI Token Names
 *
 * String constants for every CSS custom property defined in tokens.css.
 * Use these when constructing `var(TOKEN.XXX)` references in TypeScript
 * to get autocomplete and prevent typos in token names.
 *
 * Usage:
 *   import { TOKEN } from "@galley/shared-ui-tokens";
 *   style={{ color: `var(${TOKEN.TEXT_PRIMARY})` }}
 */

// ── Surfaces ──────────────────────────────────────────────────────────────────

export const BG = {
  BASE:     "--bg-base",
  GRAPHITE: "--bg-graphite",
  PANEL:    "--bg-panel",
  FIELD:    "--bg-field",
  OVERLAY:  "--bg-overlay",
} as const;

// ── Text ──────────────────────────────────────────────────────────────────────

export const TEXT = {
  PRIMARY:     "--text-primary",
  SECONDARY:   "--text-secondary",
  TERTIARY:    "--text-tertiary",
  INVERSE:     "--text-inverse",
  PLACEHOLDER: "--text-placeholder",
} as const;

// ── Borders / Seams ───────────────────────────────────────────────────────────

export const BORDER = {
  SUBTLE:  "--border-subtle",
  PRIMARY: "--border-primary",
  FOCUS:   "--border-focus",
} as const;

// ── State / Signal ────────────────────────────────────────────────────────────

export const STATE = {
  VERIFIED:     "--state-verified",
  ADVISORY:     "--state-advisory",
  ERROR:        "--state-error",
  FAVORITE:     "--state-favorite",
  ARCHIVED:     "--state-archived",
  INFO:         "--state-info",
  VERIFIED_BG:  "--state-verified-bg",
  ADVISORY_BG:  "--state-advisory-bg",
  ERROR_BG:     "--state-error-bg",
  ARCHIVED_BG:  "--state-archived-bg",
} as const;

// ── Typography — families ─────────────────────────────────────────────────────

export const FONT = {
  DISPLAY: "--font-display",
  BODY:    "--font-body",
  UTILITY: "--font-utility",
  NUMERIC: "--font-numeric",
} as const;

// ── Typography — scale ────────────────────────────────────────────────────────

export const TEXT_SIZE = {
  XS:   "--text-xs",
  SM:   "--text-sm",
  BASE: "--text-base",
  MD:   "--text-md",
  LG:   "--text-lg",
  XL:   "--text-xl",
  "2XL": "--text-2xl",
  "3XL": "--text-3xl",
} as const;

export const LEADING = {
  TIGHT:   "--leading-tight",
  SNUG:    "--leading-snug",
  NORMAL:  "--leading-normal",
  RELAXED: "--leading-relaxed",
} as const;

export const TRACKING = {
  TIGHT:  "--tracking-tight",
  NORMAL: "--tracking-normal",
  WIDE:   "--tracking-wide",
  WIDER:  "--tracking-wider",
} as const;

// ── Spacing ───────────────────────────────────────────────────────────────────

export const SPACE = {
  "1":  "--space-1",
  "2":  "--space-2",
  "3":  "--space-3",
  "4":  "--space-4",
  "5":  "--space-5",
  "6":  "--space-6",
  "8":  "--space-8",
  "10": "--space-10",
  "12": "--space-12",
  "16": "--space-16",
} as const;

// ── Radii ─────────────────────────────────────────────────────────────────────

export const RADIUS = {
  SM: "--radius-sm",
  MD: "--radius-md",
  LG: "--radius-lg",
} as const;

// ── Layout ────────────────────────────────────────────────────────────────────

export const LAYOUT = {
  NAV_WIDTH:          "--nav-width",
  CONTENT_MAX:        "--content-max",
  META_STRIP_HEIGHT:  "--meta-strip-height",
} as const;

// ── Motion ────────────────────────────────────────────────────────────────────

export const TRANSITION = {
  FAST:   "--transition-fast",
  NORMAL: "--transition-normal",
} as const;

// ── Namespaced convenience export ─────────────────────────────────────────────

export const TOKEN = {
  bg:         BG,
  text:       TEXT,
  textSize:   TEXT_SIZE,
  border:     BORDER,
  state:      STATE,
  font:       FONT,
  leading:    LEADING,
  tracking:   TRACKING,
  space:      SPACE,
  radius:     RADIUS,
  layout:     LAYOUT,
  transition: TRANSITION,
} as const;

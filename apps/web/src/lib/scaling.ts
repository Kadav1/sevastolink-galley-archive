/**
 * Recipe scaling utilities — shared by Recipe Detail and Kitchen Mode.
 *
 * Scaling is a view/display behavior only.
 * No canonical recipe data is mutated.
 * Original values are always recoverable by returning to scale = 1.
 */

// ── Scale model ───────────────────────────────────────────────────────────────

export type ScaleFactor = 0.5 | 1 | 2 | 3;

export const SCALE_OPTIONS: { label: string; value: ScaleFactor }[] = [
  { label: "½×", value: 0.5 },
  { label: "1×", value: 1 },
  { label: "2×", value: 2 },
  { label: "3×", value: 3 },
];

export const DEFAULT_SCALE: ScaleFactor = 1;

// ── Fraction table ────────────────────────────────────────────────────────────

const FRACTIONS: Record<string, number> = {
  // Unicode vulgar fractions
  "½": 0.5,
  "⅓": 1 / 3, "⅔": 2 / 3,
  "¼": 0.25,  "¾": 0.75,
  "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875,
  // ASCII slash fractions
  "1/2": 0.5,
  "1/3": 1 / 3, "2/3": 2 / 3,
  "1/4": 0.25,  "3/4": 0.75,
  "1/8": 0.125,
};

// Common fractions for output formatting, sorted by value descending
// (so we match the closest fraction when there are rounding artifacts)
const FORMAT_FRACTIONS: [number, string][] = [
  [0.875, "⅞"], [0.75, "¾"], [0.625, "⅝"],
  [0.5, "½"], [0.375, "⅜"], [0.25, "¼"], [0.125, "⅛"],
  [2 / 3, "⅔"], [1 / 3, "⅓"],
];

// ── Parsing ───────────────────────────────────────────────────────────────────

function parseFraction(s: string): number | null {
  const f = FRACTIONS[s];
  if (f !== undefined) return f;
  const m = s.match(/^(\d+)\/(\d+)$/);
  if (m) {
    const n = parseInt(m[1]);
    const d = parseInt(m[2]);
    if (d === 0) return null;
    return n / d;
  }
  return null;
}

/**
 * Parse a quantity string to a decimal number.
 * Handles: integers, decimals, Unicode fractions, ASCII fractions,
 * and mixed "whole fraction" forms like "1 ½" or "2 1/4".
 * Returns null if the string cannot be parsed as a number.
 */
export function parseQuantity(q: string): number | null {
  const s = q.trim();
  if (!s) return null;

  // Pure integer or decimal (strict: "2", "1.5" but not "2 tbsp")
  const num = parseFloat(s);
  if (!isNaN(num) && String(num) === s) return num;

  // Single fraction
  const frac = parseFraction(s);
  if (frac !== null) return frac;

  // "whole fraction" form: "1 ½", "2 1/4"
  const spaceIdx = s.indexOf(" ");
  if (spaceIdx > 0) {
    const wholePart = s.slice(0, spaceIdx);
    const fracPart = s.slice(spaceIdx + 1);
    const wholeNum = parseFloat(wholePart);
    const fracNum = parseFraction(fracPart);
    if (!isNaN(wholeNum) && wholeNum >= 0 && fracNum !== null) {
      return wholeNum + fracNum;
    }
  }

  return null;
}

// ── Formatting ────────────────────────────────────────────────────────────────

/**
 * Format a decimal number back to a clean quantity string.
 * Prefers Unicode fractions for common values; falls back to 1 decimal place.
 */
export function formatNumber(n: number): string {
  if (n <= 0) return "0";

  const whole = Math.floor(n);
  const frac = n - whole;

  // Integer result
  if (Math.abs(frac) < 0.01) return String(Math.round(n));

  // Try to match fractional part to a common fraction
  for (const [val, sym] of FORMAT_FRACTIONS) {
    if (Math.abs(frac - val) < 0.013) {
      return whole > 0 ? `${whole} ${sym}` : sym;
    }
  }

  // Decimal fallback
  return n.toFixed(1).replace(/\.0$/, "");
}

// ── Quantity scaling ──────────────────────────────────────────────────────────

/**
 * Scale a raw quantity string by `scale`.
 * Returns { display, scaled } where `scaled` is false if:
 * - scale === 1 (no change needed)
 * - quantity string could not be parsed as a number
 */
export function scaleQuantity(
  raw: string | null | undefined,
  scale: ScaleFactor,
): { display: string; scaled: boolean } {
  if (raw == null || raw.trim() === "") return { display: "", scaled: false };
  if (scale === 1) return { display: raw, scaled: false };

  const n = parseQuantity(raw);
  if (n === null) return { display: raw, scaled: false };

  return { display: formatNumber(n * scale), scaled: true };
}

// ── Servings scaling ──────────────────────────────────────────────────────────

/**
 * Scale a servings string (e.g. "4", "4–6", "serves 4") by `scale`.
 * Handles plain numbers, ranges (4-6, 4–6), and falls back to annotation.
 */
export function scaleServings(raw: string, scale: ScaleFactor): string {
  if (scale === 1) return raw;

  function fmt(n: number): string {
    return n % 1 === 0 ? String(Math.round(n)) : n.toFixed(1);
  }

  // Range: "4-6" or "4–6"
  const rangeMatch = raw.match(/^(\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)(.*)$/);
  if (rangeMatch) {
    const lo = parseFloat(rangeMatch[1]) * scale;
    const hi = parseFloat(rangeMatch[2]) * scale;
    const sep = raw.includes("–") ? "–" : "-";
    return `${fmt(lo)}${sep}${fmt(hi)}${rangeMatch[3]}`;
  }

  // Plain number possibly followed by label text (e.g. "4 portions")
  const numMatch = raw.match(/^(\d+(?:\.\d+)?)(.*)/);
  if (numMatch) {
    const scaled = parseFloat(numMatch[1]) * scale;
    return `${fmt(scaled)}${numMatch[2]}`;
  }

  // Non-numeric — annotate
  return `${raw} (×${scale})`;
}

// ── Step instruction scaling ──────────────────────────────────────────────────

/**
 * Recognized cooking units for step-text scanning.
 * Only quantities followed by one of these units are scaled.
 * Ordered longest-first so the regex engine prefers specific matches.
 */
const STEP_UNITS = [
  "tablespoons?", "teaspoons?",
  "kilograms?", "milligrams?", "millilitres?", "milliliters?",
  "litres?", "liters?",
  "ounces?", "pounds?",
  "grams?",
  "tbsp", "Tbsp", "tsp",
  "cups?",
  "fl\\.?\\s*oz",
  "kg", "ml", "mg",
  "dl", "cl",
  "lbs?", "lb",
  "oz",
  "g", "l",
].join("|");

// Matches: (number-or-fraction) optionally-preceded-by-whole-number, then a unit word.
// The quantity part handles: integers, decimals, unicode fractions, ASCII fractions, mixed forms.
const STEP_QTY_RE = new RegExp(
  `\\b((?:\\d+\\s+)?(?:[½⅓⅔¼¾⅛⅜⅝⅞]|\\d+\\/\\d+|\\d+(?:\\.\\d+)?))\\s*(${STEP_UNITS})\\b`,
  "g",
);

/**
 * Scan a step instruction for quantity+unit patterns and scale each one.
 * Returns the modified text and whether any quantities were actually scaled.
 *
 * Only quantities attached to a recognized cooking unit are scaled.
 * Quantities that cannot be parsed are left untouched.
 * At scale === 1, returns the original string unchanged.
 */
export function scaleStepText(
  instruction: string,
  scale: ScaleFactor,
): { text: string; scaled: boolean } {
  if (scale === 1) return { text: instruction, scaled: false };

  let anyScaled = false;
  const text = instruction.replace(STEP_QTY_RE, (match, numStr: string, unit: string) => {
    const n = parseQuantity(numStr.trim());
    if (n === null) return match;
    anyScaled = true;
    return `${formatNumber(n * scale)} ${unit}`;
  });

  return { text, scaled: anyScaled };
}


// ── Display text builder ──────────────────────────────────────────────────────

export interface ScaledIngredientParts {
  quantity: string;
  unit: string | null;
  item: string;
  preparation: string | null;
  quantityScaled: boolean;
  /** True if this ingredient has only a display_text (no structured data to scale) */
  displayTextOnly: boolean;
}

import type { Ingredient } from "../types/recipe";

/**
 * Build structured display parts for an ingredient at a given scale.
 * When scale === 1 and display_text is present, uses display_text verbatim.
 * When scaling, always uses structured quantity/unit/item fields.
 */
export function buildIngredientParts(
  ing: Ingredient,
  scale: ScaleFactor,
): ScaledIngredientParts {
  // At 1× with display_text, preserve the author's text exactly
  if (ing.display_text && scale === 1) {
    return {
      quantity: ing.display_text,
      unit: null,
      item: "",
      preparation: null,
      quantityScaled: false,
      displayTextOnly: true,
    };
  }

  const { display: scaledQty, scaled } = scaleQuantity(ing.quantity, scale);

  return {
    quantity: scaledQty,
    unit: ing.unit,
    item: ing.item,
    preparation: ing.preparation,
    quantityScaled: scaled,
    displayTextOnly: false,
  };
}

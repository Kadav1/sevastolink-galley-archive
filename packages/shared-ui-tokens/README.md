# Sevastolink Galley Archive

## Shared UI Tokens Package v1.0

---

## 1. Purpose

This package defines the shared UI token layer used by the frontend.

It establishes:

* the token source files
* the exported token name constants
* how the frontend should consume shared token names
* the boundary between token definition and component styling

This package is the shared naming layer for the current Sevastolink visual system implementation.

---

## 2. Package role

### Established facts

* Token CSS lives in `tokens.css`.
* TypeScript token-name constants live in `src/index.ts`.
* The web app uses CSS custom properties directly in component styles.

### Current standard

This package should provide:

* stable token names
* a single source for token identifiers
* enough structure to reduce token name drift in TypeScript code

It does not own component design decisions by itself.

---

## 3. Current contents

The package currently provides:

* `tokens.css` — shared CSS custom property definitions
* `src/index.ts` — grouped token-name exports such as `BG`, `TEXT`, `BORDER`, `STATE`, `FONT`, and `TOKEN`

---

## 4. Usage guidance

Frontend code may consume token names through the TypeScript exports when building style objects, for example:

* `var(${TOKEN.text.PRIMARY})`
* `var(${TOKEN.space["4"]})`

This improves autocomplete and reduces typo risk in token references.

---

## 5. Change guidance

When changing tokens:

1. update the CSS custom property source in `tokens.css`
2. update the corresponding token-name exports in `src/index.ts`
3. verify that consuming frontend code still references valid token names

### Current warning

Do not rename shared token identifiers casually. A token rename can silently break multiple components even when the visual design intent remains unchanged.

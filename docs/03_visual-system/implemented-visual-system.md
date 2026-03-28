# Sevastolink Galley Archive

## Implemented Visual System v1.0

---

## 1. Purpose

This document defines the visual-system implementation that currently exists in the repository.

It establishes:

* the token layer that is implemented today
* the global styling primitives that are active in the web app
* which visual-system areas are already reflected in component code
* which parts of the broader visual spec have not yet been implemented

This is the implementation-aware visual baseline for contributors.

---

## 2. Current implementation baseline

### Established facts

The current frontend implements:

* a shared CSS-token layer in `packages/shared-ui-tokens/tokens.css`
* a web token import shim in `apps/web/src/styles/tokens.css`
* global base styling in `apps/web/src/styles/global.css`
* a single dark visual direction aligned with the archive-first design language
* kitchen-mode token overrides through `[data-mode="kitchen"]`

The current frontend does not yet implement:

* a fuller responsive layout system across desktop, tablet, and mobile breakpoints
* overlay, drawer, sheet, or modal surfaces using the defined overlay tokens
* a reusable component primitive library derived from the visual rules
* TypeScript token-name usage through `@galley/shared-ui-tokens` in component code

---

## 3. Implemented token layer

### 3.1 Shared token source

The canonical implemented token file is:

* `packages/shared-ui-tokens/tokens.css`

This file currently defines:

* surface tokens
* text tokens
* border tokens
* state and signal tokens
* typography tokens
* spacing tokens
* radius tokens
* layout tokens
* transition tokens

### 3.2 Web consumption

The web app consumes the shared token file through:

* `apps/web/src/styles/tokens.css`
* `apps/web/src/styles/global.css`

Current implementation standard:

* component styles use CSS custom properties directly
* the token package is implemented as CSS first
* TypeScript token-name exports exist, but are not yet used in component code

---

## 4. Implemented visual direction

### Established facts

The current app already reflects the strongest archive-first direction from the visual spec in broad terms:

* dark shell and working surfaces
* restrained type and spacing
* quiet status language
* low-saturation signal colors
* metadata-led hierarchy

This is visible in:

* shell and navigation surfaces
* recipe metadata strip
* library rows and filters
* kitchen-mode typography and spacing

### Current interpretation

The repository has one concrete implemented visual direction today, not multiple switchable visual variants.

The “three directions” section in the broader visual spec should therefore be read as design history and decision context, not as multiple live themes.

---

## 5. Implemented component styling patterns

### 5.1 Shell

The current shell implements:

* left navigation rail
* dark shell/background split
* main content pane

It does not yet implement:

* right context rail
* top shell action/search zone
* alternative shell variants beyond kitchen mode leaving the shell

### 5.2 Inputs and controls

The current app implements consistent styling for:

* text inputs
* textareas
* selects
* quiet inline buttons
* chip-like filter controls

This styling is currently expressed directly in page and component style objects rather than through a reusable primitive component set.

### 5.3 Status and metadata

The current app implements:

* status badge treatment for trust state
* metadata strip treatment on recipe detail
* quiet utility labels and metadata rows

### 5.4 Kitchen mode

The current app implements:

* kitchen-mode token overrides
* larger typography
* increased spacing
* reduced shell chrome

Kitchen mode is the clearest area where the visual-system spec has already been translated into concrete runtime behavior.

---

## 6. Current gaps relative to the full visual spec

The broader visual-system spec describes more than the current frontend has implemented.

Not yet materially implemented:

* responsive breakpoint-specific layout behavior
* overlay, drawer, modal, and sheet surfaces
* richer recipe-card design patterns beyond the current row-based library list
* a formal button class system
* iconography rules expressed through a real icon set
* image handling surfaces
* reusable visual primitives for component-level consistency

---

## 7. Contributor note

When changing frontend styling:

* treat this document as the current implementation baseline
* treat `visual-system-spec.md` as the broader target-state visual reference
* update token docs when shared token names or semantics change
* avoid documenting a spec-only visual surface as implemented until it exists in the UI

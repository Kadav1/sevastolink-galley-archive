# Sevastolink Galley Archive

## Visual System Implementation Backlog v1.0

---

## 1. Purpose

This document translates `docs/03_visual-system/visual-system-spec.md` into a concrete implementation backlog.

It establishes:

* which visual-system areas are already implemented
* which target-state visual areas are still missing
* which missing work should be prioritized first
* how the missing work maps back to the current visual spec

This is an implementation-planning document for the frontend visual layer.

---

## 2. Current implementation baseline

Already implemented:

* shared CSS token source
* global type and form baseline
* dark archive-first palette direction
* metadata-led styling patterns
* trust-state badges
* kitchen-mode token overrides

Still missing:

* responsive layout behavior beyond the current default layouts
* visual primitives for overlays and transient surfaces
* reusable button/input/card primitives
* richer library card/view patterns
* iconography system
* image handling surfaces
* consistent token usage through TypeScript helpers

---

## 3. Backlog summary

| Priority | Area | Current state | Target state | Spec section |
|---|---|---|---|---|
| P1 | Responsive layout system | Mostly fixed layout assumptions | Desktop, tablet, and mobile behavior aligned with spec | `§5` |
| P1 | Reusable visual primitives | Inline styles repeated across components | Shared buttons, inputs, panels, chips, labels | `§7`, `§8`, `§9`, `§13` |
| P1 | Library visual expansion | Row-based list only | Stronger recipe-card and library context patterns | `§10` |
| P2 | Overlay and transient surfaces | Tokens exist, surfaces do not | Drawers, overlays, modals, sheets | `§6`, `§7` |
| P2 | Settings and AI visual patterns | Route surfaces missing or placeholder | Distinct visual patterns for settings and AI tools | `§8`, `§9`, `§13` |
| P2 | Iconography system | No formal icon system | Quiet operational icon language | `§14` |
| P3 | Image handling system | No current image surfaces | Controlled image usage rules in UI | `§15` |
| P3 | TS token helper adoption | Token constants defined but unused | Typed token references in component code | package + token-consumer alignment |

---

## 4. Backlog detail

### 4.1 P1: Responsive layout system

Current state:

* shell and pages rely mostly on static flex layouts and fixed widths
* there are no meaningful frontend media-query breakpoints in the current app styles

Missing target-state items:

* desktop, tablet, and mobile layout variants
* collapsible or adaptive side-rail behavior
* stronger vertical stacking on smaller screens
* cooking-oriented mobile/tablet adjustments outside kitchen mode

Likely implementation work:

* add shared responsive layout rules to global or token-adjacent CSS
* audit pages with fixed widths and rail assumptions
* define breakpoint standards before adding more screens

Primary source:

* `visual-system-spec.md` §5

### 4.2 P1: Reusable visual primitives

Current state:

* most components use inline style objects
* inputs, chips, labels, panels, and buttons are visually similar but not abstracted into shared primitives

Missing target-state items:

* shared panel primitive
* shared button variants
* shared field/input primitives
* shared label and section-heading primitives
* shared advisory/status treatment patterns

Likely implementation work:

* extract the most repeated visual patterns from existing components
* build only primitives that already have multiple consumers
* align names with the visual spec instead of ad hoc component-local naming

Primary source:

* `visual-system-spec.md` §7
* `visual-system-spec.md` §8
* `visual-system-spec.md` §9
* `visual-system-spec.md` §13

### 4.3 P1: Library visual expansion

Current state:

* the library is row-based and functional
* it uses search, filters, quiet metadata, and trust-state cues

Missing target-state items:

* stronger recipe-card language where appropriate
* route-context-specific library views
* clearer library-context hierarchy when favorites, drafts, verified, or search-result views are added

Likely implementation work:

* defer broad card-system work until route expansion lands
* define whether the library remains row-first or mixes rows and cards by context
* preserve the operational archive tone rather than drifting into generic SaaS cards

Primary source:

* `visual-system-spec.md` §10

### 4.4 P2: Overlay and transient surfaces

Current state:

* overlay tokens exist
* no actual modal, sheet, drawer, or overlay UI surfaces are implemented

Missing target-state items:

* modals
* drawers
* transient review and settings surfaces
* filter sheets for smaller screens

Likely implementation work:

* introduce one overlay primitive first
* define seam, density, and spacing rules in actual code
* connect overlay work to the first real workflow that needs it

Primary source:

* `visual-system-spec.md` §6
* `visual-system-spec.md` §7

### 4.5 P2: Settings and AI visual patterns

Current state:

* settings is a placeholder
* AI exists only inside paste-text intake

Missing target-state items:

* visual patterns for grouped settings surfaces
* visual patterns for AI advisory/review surfaces
* stronger distinction between archive content and assistive tooling

Likely implementation work:

* build these only after the underlying routes exist
* reuse the advisory and metadata logic already present in the current app

Primary source:

* `visual-system-spec.md` §8
* `visual-system-spec.md` §9
* `visual-system-spec.md` §13

### 4.6 P2: Iconography system

Current state:

* the UI currently relies mostly on text labels and a few literal characters

Missing target-state items:

* a defined icon set
* rules for icon usage and density
* icon treatment consistent with the quiet operational tone

Likely implementation work:

* choose or build a restrained icon set
* apply it only where it improves recognition or scanning

Primary source:

* `visual-system-spec.md` §14

### 4.7 P3: Image handling system

Current state:

* the current app is almost entirely text- and metadata-driven
* no meaningful image surfaces are implemented

Missing target-state items:

* image handling rules expressed in real UI
* source imagery or recipe-image treatments if adopted later

Primary source:

* `visual-system-spec.md` §15

### 4.8 P3: TypeScript token helper adoption

Current state:

* `packages/shared-ui-tokens/src/index.ts` exports token-name constants
* frontend component code does not currently consume them

Missing target-state items:

* typed token references where TypeScript styles are constructed dynamically

Likely implementation work:

* adopt token-name helpers only where they reduce drift
* avoid churn-only refactors that replace readable `var(--token)` strings without adding practical value

Primary source:

* `packages/shared-ui-tokens/README.md`

---

## 5. Recommended implementation order

### Phase 1

Build the structural visual foundations that will support later UX expansion:

* responsive layout rules
* reusable visual primitives
* library visual refinement

### Phase 2

Add the visual surfaces needed by missing product areas:

* overlays and transient surfaces
* settings visual system
* AI visual system
* iconography

### Phase 3

Complete lower-priority support areas:

* image handling
* targeted TS token-helper adoption

---

## 6. Contributor rule

When implementing against the visual-system docs:

* treat `implemented-visual-system.md` as the current-state truth
* treat `visual-system-spec.md` as the broader target-state design reference
* move backlog items into the implemented doc only when they materially exist in the app

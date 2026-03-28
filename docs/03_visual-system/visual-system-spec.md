# Sevastolink Galley Archive

## Visual System Spec v2.0

## 1. Purpose

This document translates Sevastolink into a complete UI language for Sevastolink Galley Archive.

It establishes:

* the visual design principles for the product
* the semantic palette and surface hierarchy
* typography, layout, and grid behavior
* component-level styling rules
* recipe-specific and kitchen-specific visual standards
* accessibility and readability constraints
* three viable visual directions
* the final recommended visual direction

This is the canonical target-state visual source of truth for the product.

Current implementation note:

* the repository already implements the core shared token layer, global visual baseline, and kitchen-mode overrides
* the repository does not yet implement every layout, component, and transient-surface pattern described here
* use `docs/03_visual-system/implemented-visual-system.md` for the current implementation baseline
* use `docs/03_visual-system/implementation-backlog.md` for the prioritized target-state gap list

---

## Current-state gap note

Implemented today:

* shared CSS token source
* global dark visual baseline
* quiet archive-first palette and typography direction
* metadata-led recipe styling patterns
* kitchen-mode token overrides

Not yet fully implemented today:

* responsive breakpoint-specific layout behavior
* reusable visual primitives for buttons, panels, and overlays
* overlay, drawer, modal, and sheet surfaces
* iconography system
* image handling surfaces
* broad component-level adoption of the TypeScript token helper layer

The remainder of this document should therefore be read as target-state visual guidance rather than as a complete description of the current frontend.

---

## 2. Visual design principles

### Established facts

The product must feel:

* premium
* dark
* infrastructural
* calm
* operational
* precise

The product must not feel:

* like a literal terminal
* like a fake spaceship panel
* like cyberpunk neon
* like a gaming dashboard
* like a generic recipe SaaS

### Design principles

#### 2.1 Archive first

The interface should feel like a domestic archive and working system, not a content feed.

#### 2.2 Structure over performance

Hierarchy, spacing, seams, and metadata carry the identity more than decoration does.

#### 2.3 Dark without spectacle

The product should be dark through tonal control, not through glow effects, neon accents, or theatrical contrast.

#### 2.4 Premium through discipline

The premium quality comes from measured spacing, consistent type, material restraint, and strong information rhythm.

#### 2.5 Operational calm

Controls, states, and metadata should feel reliable and quiet. No part of the UI should appear frantic.

#### 2.6 Kitchen readability is mandatory

The visual system must remain usable under cooking conditions:

* partial attention
* messy hands
* variable lighting
* arm’s-length reading

---

## 3. Palette with semantic roles

### 3.1 Surface roles

Use semantic roles, not decorative swatches.

| Role | Purpose |
|---|---|
| `bg/base` | Deepest app shell and page background |
| `bg/graphite` | Main working canvas |
| `bg/panel` | Primary modules, cards, drawers, side panels |
| `bg/field` | Inputs, subpanels, embedded utility surfaces |
| `bg/overlay` | Modal and elevated transient surfaces |

### 3.2 Text roles

| Role | Purpose |
|---|---|
| `text/primary` | Titles, body text, ingredients, method |
| `text/secondary` | Supporting labels, descriptions, moderate metadata |
| `text/tertiary` | Timestamps, technical tags, low-priority utility text |
| `text/inverse` | Rare high-contrast text on signal surfaces |

### 3.3 Border and seam roles

| Role | Purpose |
|---|---|
| `border/subtle` | Internal seams, low-noise module separation |
| `border/primary` | Stronger field and panel definition |
| `border/focus` | Keyboard and active focus indication |

### 3.4 State and signal roles

| Role | Purpose |
|---|---|
| `state/verified` | Verified, trusted, confirmed |
| `state/advisory` | Review, in-progress, caution, AI suggestion |
| `state/error` | Faults, destructive actions, invalid states |
| `state/favorite` | Favorite marker |
| `state/archived` | Archived or inactive content |
| `state/info-neutral` | Quiet supporting system cues |

### 3.5 Palette behavior rules

* Most of the interface should rely on tonal layering and type contrast, not accent saturation.
* Signal green should indicate trust and active confirmation, not decoration.
* Amber should indicate advisory or in-review states, never panic.
* Red should remain rare and reserved for destructive or error states.
* Blue-grey neutrals may be used for passive informational structure but must not dominate.

### 3.6 Palette direction

Recommended tonal family:

* near-black shell
* graphite working ground
* slightly warmer charcoal panels
* muted bone-grey text
* restrained green and amber signals

Avoid:

* purple
* electric cyan
* acid green
* luminous gradients
* glossy metallic effects

---

## 4. Typography roles

### 4.1 Display

Used for:

* recipe titles
* page titles
* major screen headers

Characteristics:

* composed
* premium
* restrained
* slightly condensed or tightly controlled

### 4.2 Section label

Used for:

* module headers
* metadata group labels
* settings section labels
* archive rail labels

Characteristics:

* compact
* slightly tracked
* uppercase or near-uppercase
* low-noise

### 4.3 Body

Used for:

* steps
* notes
* descriptions
* recipe detail text

Characteristics:

* highly legible
* moderate line height
* optimized for extended reading

### 4.4 Utility

Used for:

* timestamps
* source markers
* state labels
* small metadata

Characteristics:

* compact
* understated
* still readable

### 4.5 Numeric accent

Used sparingly for:

* timings
* yields
* ratings
* counts

Characteristics:

* slightly more mechanical
* may use a mono-adjacent family
* must not dominate body reading

### 4.6 Typography rules

* Do not use mono as the global UI voice.
* Method text should always privilege legibility over aesthetic posture.
* Titles should feel stable and composed, not editorially dramatic.
* Kitchen Mode must increase type size and spacing significantly.
* Avoid soft luxury serif language that weakens the technical identity.

---

## 5. Layout / grid logic

### 5.1 Core layout principle

The layout should feel infrastructural: clear shell, clear panels, clear reading lanes.

### 5.2 Grid behavior

#### Desktop

Preferred grid:

* left rail for nav and structural controls
* central content column
* optional right context rail

Use wider reading lanes for recipe detail and narrower support rails for metadata and source.

#### Tablet

Prefer:

* simplified two-zone layouts
* collapsible side rails
* stronger vertical stacking in portrait

Tablet is a primary cooking device, so readability and touch spacing take precedence over density.

#### Mobile

Prefer:

* single-column stacks
* slide-over sheets for filters and support panels
* sticky bottom action zones where useful

Do not simulate desktop density on mobile.

### 5.3 Spacing logic

Base scale should use a restrained modular rhythm:

* `4`
* `8`
* `12`
* `16`
* `24`
* `32`
* `40`
* `48`
* `64`

### 5.4 Layout rules

* Use wide spacing for screen grouping and title-to-content transitions.
* Use compact spacing for metadata strips and utility rows.
* Keep forms and review screens structured, not loose.
* Kitchen Mode gets larger vertical gaps and larger touch-safe spacing.

---

## 6. Surface hierarchy

### Surface levels

| Level | Purpose |
|---|---|
| `L0` | App shell and page ground |
| `L1` | Main content regions |
| `L2` | Modules such as cards, sections, rails |
| `L3` | Embedded utility surfaces such as fields and strips |
| `L4` | Overlays, drawers, modals |

### Surface rules

* Each level should be distinguished by tone, seam, and spacing before shadow.
* Elevated overlays should feel dense and precise, not floaty.
* Cards should feel like contained archive modules, not generic rounded blobs.
* The shell should feel grounded and persistent.

---

## 7. Divider / seam logic

### Seam role

Dividers are a core part of the Sevastolink language. They should feel like panel seams and structural boundaries.

### Rules

* Use thin, deliberate lines.
* Prefer seams over heavy boxes.
* Internal section breaks should be quieter than panel boundaries.
* Do not over-grid the UI with visible lines everywhere.

### Usage

Use seams for:

* metadata row separation
* recipe section boundaries
* rail boundaries
* drawer and overlay structure
* intake source vs candidate separation

Avoid:

* ornamental borders
* double-line separators
* glowing or animated dividers

---

## 8. Metadata strip logic

### Role

The metadata strip is one of the signature Sevastolink components.

### Purpose

Present recipe-critical data as an operational band:

* dish role
* cuisine
* technique
* timings
* servings
* complexity
* heat window
* trust state

### Structure rules

* Use consistent label/value rhythm.
* Keep ordering stable across recipes.
* Separate groups with subtle seams or controlled spacing.
* Avoid turning every field into a colored badge.

### Tone

The strip should feel like archive data and culinary telemetry, not like a dashboard widget.

---

## 9. Button / input patterns

### 9.1 Button classes

Use these button classes:

* `Primary`
* `Secondary`
* `Utility`
* `Destructive`
* `Quiet / Inline`

### 9.2 Button rules

* Primary buttons should feel decisive but calm.
* Destructive buttons must be unmistakable and rare.
* Inline actions should not collapse into low-contrast invisibility.
* AI actions must not visually outrank core archive actions.

### 9.3 Input rules

* Labels must always be visible.
* Inputs need strong focus treatment.
* Field groups must be clearly separated.
* Long-form editing must not feel cramped.
* Raw source, structured candidate, and approved fields must not share identical styling when shown together.

### 9.4 Search input

Search should feel:

* primary
* stable
* easy to locate
* strong enough to anchor archive retrieval

---

## 10. Recipe card design rules

### Content hierarchy

1. Title
2. Core metadata
3. Secondary descriptor or note
4. Optional image

### Required content

* title
* role / cuisine / technique summary
* time and yield
* trust and favorite state
* optional image

### Rules

* Title must dominate the card.
* Metadata must remain structured and scannable.
* Images must never overwhelm retrieval usefulness.
* Cards should read quickly in both list and compact grid contexts.
* Trust state must be visible without opening the recipe.

### Recommendation

Prefer list rows or compact cards over visually rich large-card layouts for the main archive view.

---

## 11. Recipe detail page design rules

### Role

Recipe detail pages should feel like dossiers.

### Required immediate visibility

When a recipe opens, the user must immediately see:

* title
* trust / verification state
* metadata strip
* ingredients entry point
* method entry point
* Kitchen Mode action
* source / provenance access

### Page hierarchy

* title and action zone
* metadata strip
* ingredients
* method
* notes / service guidance
* source / trust / revision layer

### Rules

* Ingredients and steps are the strongest reading surfaces.
* Notes should feel integrated, not appended as leftovers.
* Source and revision data should sit lower in hierarchy.
* AI actions should appear as secondary support controls.
* Images are supportive, not dominant.

---

## 12. Kitchen mode design rules

### Role

Kitchen Mode is a reduced operational state, not a decorative variant.

### Rules

* fewer surfaces
* larger type
* stronger contrast
* larger touch targets
* reduced metadata clutter
* stable previous / next controls
* clear ingredient access without losing step position

### Visual priorities

* current step readability
* ingredient legibility
* step progress clarity
* low visual fatigue

### Prohibitions

Do not use:

* small tabs
* dense accordions
* tiny metadata
* decorative overlays
* unnecessary side panels on narrow screens

---

## 13. Status and advisory styling rules

### Status classes

Use visual states for:

* Verified
* Draft
* Unverified
* Archived
* Favorite
* Revised
* AI Suggested
* AI Accepted
* AI Edited

### Rules

* Status must not rely on color alone.
* Verification and archive states should be readable in monochrome fallback.
* Advisory states should use amber or neutral support, not aggressive warning language.
* Error states should be concise and rare.
* AI suggestion states must remain visually distinct from approved archive data.

---

## 14. Iconography direction

### Direction

Icons should feel:

* restrained
* technical
* legible
* mature
* low-noise

### Rules

* Use strong silhouettes.
* Keep internal detail minimal.
* Maintain consistent stroke logic.
* Pair icon and text where clarity matters.
* Avoid playful or futuristic glyphs.

### Avoid

* sci-fi targeting marks
* pseudo-terminal symbols as decoration
* glossy app-store icon language

---

## 15. Image handling rules

### Role of images

Images support memory and dish recognition. They do not define the product.

### Rules

* Images should be optional in most archive contexts.
* Use controlled cropping and calm framing.
* Avoid turning the library into a visual feed.
* In cards, images should support title recognition, not overpower metadata.
* In Recipe Detail, images should sit above or beside content without displacing ingredients and method.

### Recommendation

For v1, support restrained image usage and keep photo management secondary to archive structure.

---

## 16. Accessibility / readability rules

### Global rules

* Body copy must maintain strong contrast on dark surfaces.
* Targets must be touch-safe on tablet and mobile.
* Text should not rely on thin weights.
* Dense metadata must still be readable at normal viewing distance.

### Kitchen-specific rules

* Large type
* larger line height
* large controls
* stable control placement
* readable at arm’s length

### Semantic rules

* Lists should remain true lists for ingredients and steps.
* Status must have text labels, not color only.
* Focus states must be visible and persistent.
* Error and advisory content must use plain language.

---

## 17. Three UI directions

### 17.1 Safest

Characteristics:

* dark neutral shell
* minimal accent color
* strong typography and spacing
* very restrained seams

Strengths:

* easiest to maintain
* lowest risk of gimmick
* highly practical

Weaknesses:

* may drift too close to a generic premium productivity tool

### 17.2 Strongest

Characteristics:

* pronounced metadata strips
* clearer seam logic
* stronger archive rail identity
* more visible operational labels

Strengths:

* most clearly expresses Sevastolink as a distinct archive system
* still practical
* strongest archive-first tone

Weaknesses:

* requires tighter discipline to avoid visual overstatement

### 17.3 Most atmospheric

Characteristics:

* darker tonal range
* more material depth
* slightly moodier panels
* more cinematic spacing and transitions

Strengths:

* strongest atmosphere
* most distinctive emotional identity

Weaknesses:

* easiest to overdecorate
* highest risk of harming kitchen usability

---

## 18. Final recommended direction

The recommended direction is **Strongest**.

### Why

It best balances:

* distinct Sevastolink identity
* archive-first structure
* premium feel
* kitchen usability
* low long-term fatigue

### Recommendation summary

Use:

* dark tonal shell
* disciplined panel hierarchy
* strong metadata strip logic
* clear seams and rails
* premium but restrained typography
* very limited accent use

Do not use:

* literal terminal styling
* cyberpunk glow
* gaming dashboard density
* decorative telemetry clutter
* oversized decorative imagery

---

## 19. Final standard

Any visual decision for Sevastolink Galley Archive should be judged by this question:

**Does this make the archive feel more trustworthy, more readable, and more operational without turning it into a gimmick?**

If not, it does not belong in the visual system.

---

## Decisions made

1. The visual language is dark, premium, infrastructural, calm, operational, and precise.
2. Sevastolink is expressed through surface hierarchy, seams, metadata rhythm, and disciplined typography rather than terminal theatrics.
3. Kitchen readability is treated as a hard visual constraint, not a secondary variant.
4. Images are supportive and optional, never the organizing principle of the product.
5. The recommended direction is the strongest archive-first direction rather than the safest generic direction or the most atmospheric direction.

## Open questions

1. Which exact typefaces should be chosen for display, body, and utility roles?
2. Should recipe cards default to list rows or compact cards in the main archive view?
3. How much image presence is appropriate on tablet Recipe Detail without weakening ingredient and method visibility?
4. Should Kitchen Mode always suppress imagery entirely?

## Deliverables created

1. `/docs/03_visual-system/visual-system-spec.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how the local-first product is run, configured, packaged, and optionally exposed on a home local network, including how the UI and optional LM Studio integration behave in local deployment.

# Sevastolink Galley Archive

## Screen Blueprint Pack v1.0

---

## 1. Purpose

This document defines blueprint-level screen structures for the first serious version of Sevastolink Galley Archive.

It establishes:

* the core screen set for v1
* the structure and priorities of each screen
* the required components and actions per screen
* responsive behavior across desktop, tablet, and mobile
* important states and accessibility expectations

This is the canonical target-state screen blueprint reference for product design.

Current implementation note:

* these blueprints are broader than the screens currently implemented in the app
* they should be treated as design intent, not as a literal map of shipped routes
* use `docs/02_ux/implemented-routes-and-flows.md` for the implementation-aware screen baseline

---

## Current-state gap note

Implemented today:

* library
* recipe detail
* kitchen mode
* intake hub
* manual entry
* paste-text intake
* settings placeholder

Not yet implemented today:

* AI tools screens
* URL import and file intake screens
* dedicated review queue screens
* recipe edit screens
* settings sub-pages and settings workflows
* library sub-route screens such as favorites, recent, verified, drafts, and search-results views

The remainder of this document should be read as target-state screen planning.

---

## 2. Screen blueprint method

### Established facts

* The product is archive-first.
* The interface must feel calm, dark, infrastructural, premium, and readable.
* Kitchen Mode must be highly legible and reduced.
* AI is optional and must remain subordinate to the archive.
* Review and trust boundaries are central to intake and AI workflows.

### Blueprint standard

Each screen blueprint defines:

* purpose
* user tasks
* hierarchy
* components
* actions
* responsive layout
* key states
* accessibility and legibility expectations

These are implementation-facing blueprints, not aesthetic mood boards.

---

## 3. Site / App Map

The v1 product map should be:

```text
Galley Archive
├── Library
│   ├── All Recipes
│   ├── Favorites
│   ├── Recent
│   ├── Verified
│   ├── Drafts / Unverified
│   ├── By Cuisine
│   ├── By Role
│   ├── By Technique
│   ├── By Ingredient Family
│   └── Search Results
├── Recipe
│   ├── Overview
│   ├── Ingredients
│   ├── Method
│   ├── Notes / Service
│   ├── Source / Status
│   └── Revision / History
├── Kitchen Mode
├── Intake / Import
│   ├── Intake Hub
│   ├── Manual Entry
│   ├── Paste Text
│   ├── URL Import
│   ├── File Intake
│   └── Review / Normalize
├── AI Tools
│   ├── Normalize Recipe
│   ├── Suggest Metadata
│   ├── Rewrite Recipe
│   ├── Compare Similar
│   └── Cook from Pantry
└── Settings
    ├── Archive
    ├── UI
    ├── Kitchen Mode
    ├── Import
    ├── AI / LM Studio
    └── Backup / Export
```

### App map rule

This must read as an operational archive system, not a content feed or lifestyle app. Retrieval, recipe use, intake, and settings are the structural backbone.

---

## 4. Primary Navigation Model

### Primary navigation

The stable top-level navigation should be:

* `Library`
* `Intake`
* `AI Tools`
* `Settings`

### Navigation rules

* `Recipe Detail` is entered from Library, Intake review, or AI-assisted results.
* `Kitchen Mode` is entered only from a recipe.
* Search belongs to the Library shell rather than a separate top-level app.
* AI should remain visible as optional utility, not the center of gravity.

---

## 5. Primary User Flows

### 5.1 Find and cook

1. Open `Library`
2. Search or filter
3. Open `Recipe Detail`
4. Inspect title, trust state, ingredients, and method
5. Enter `Kitchen Mode`

### 5.2 Add from pasted text

1. Open `Intake`
2. Choose `Paste Text`
3. Paste raw source
4. Normalize manually or with AI
5. Review structured candidate against raw source
6. Save as `Draft`, `Unverified`, or `Verified`

### 5.3 Refine existing recipe

1. Open `Library`
2. Open `Recipe Detail`
3. Edit directly or request AI assistance
4. Review changes
5. Save updated recipe

### 5.4 Search and narrow

1. Open `Library`
2. Enter query
3. Apply cuisine, role, technique, trust, and ingredient-family filters
4. Open result

### 5.5 Configure local system

1. Open `Settings`
2. Adjust archive, import, kitchen, UI, or AI configuration
3. Save
4. Return to active archive workflow

---

## 6. Suggested Route Structure

```text
/                       -> /library
/library
/library/favorites
/library/recent
/library/verified
/library/drafts
/library/search

/recipe/:slug
/recipe/:slug/edit
/recipe/:slug/kitchen

/intake
/intake/manual
/intake/text
/intake/url
/intake/file
/intake/review/:id

/ai
/ai/normalize
/ai/rewrite
/ai/suggest-metadata
/ai/pantry

/settings
/settings/archive
/settings/ui
/settings/kitchen
/settings/import
/settings/ai
/settings/export
```

### Route rule

The route structure should make archive state and workflow state obvious. Intake review and Kitchen Mode are focused route states, not separate products.

---

## 7. Library

### 7.1 Screen purpose

The Library is the archive command center. Its job is to help the user find, scan, filter, and reopen recipes quickly.

### 7.2 Primary tasks

* search recipes by text
* filter by trust state, cuisine, role, technique, and operational metadata
* browse recent, favorite, verified, and draft recipes
* open a recipe detail page
* enter the intake flow

### 7.3 Information hierarchy

1. Search and top action zone
2. Filter and facet controls
3. Active library context label
4. Result list or card grid
5. Quick metadata and status indicators
6. Optional archive summary counts

### 7.4 Required components

* App shell header
* Primary navigation
* Search input
* Filter rail or filter drawer
* Result list or recipe card collection
* Status chips
* Quick metadata strip
* Empty state panel
* Loading state skeletons

### 7.5 Primary actions

* search
* apply filter
* open recipe
* clear search
* start intake

### 7.6 Secondary actions

* sort results
* mark favorite from result row if implemented
* open saved view such as Verified or Drafts
* inspect active filters

### 7.7 Desktop layout

Use a three-zone layout:

* persistent left navigation rail
* upper search and summary band
* main content area with optional left filter column and central result pane

Preferred structure:

* left rail: primary nav and library sections
* upper band: large search field, archive context label, quick action button for Intake
* center: results
* right optional narrow rail: archive stats, recent filters, or selected facet summary

### 7.8 Tablet layout

Compress to two primary columns:

* collapsible navigation/filter panel
* main result pane

Search remains pinned at top. Secondary summaries move below the search row or into collapsible modules.

### 7.9 Mobile layout

Use a stacked layout:

* top app bar
* prominent search field
* horizontal filter chips with a full-screen filter sheet
* vertically stacked result rows

Do not use dense multi-column cards on mobile for the main library view.

### 7.10 Important states

* default library
* search results
* filtered results
* no matches
* loading
* empty archive

### 7.11 Accessibility and usability notes

* Search input must be focusable immediately and clearly labeled.
* Filters must be keyboard-operable.
* Status chips and metadata must not rely on color alone.
* Result rows must preserve readable tap targets.

### 7.12 Notes for kitchen-readability where relevant

Not a kitchen-focused screen. No special kitchen scaling is required beyond baseline readability.

---

## 8. Search / Filter Experience

### 8.1 Screen purpose

Search and filtering are part of the Library experience, but they are important enough to define as their own blueprint layer.

### 8.2 Primary tasks

* search by text
* narrow by taxonomy and trust state
* inspect active filters
* recover from no-result states

### 8.3 Information hierarchy

1. Query input
2. Active filters
3. Matching results
4. Facet counts or filter availability
5. Optional AI-assisted interpretation note

### 8.4 Required components

* Search field
* Filter chips or facet controls
* Filter drawer or rail
* Active-filter summary
* Result list
* No-results state

### 8.5 Primary actions

* submit query
* apply filter
* clear single filter
* clear all filters
* open recipe

### 8.6 Secondary actions

* sort results
* save or reuse query later if supported
* use AI query interpretation where available

### 8.7 Desktop layout

Keep search in the top band with filters in a left rail or docked panel and results in the central pane.

### 8.8 Tablet layout

Use a pinned search row with collapsible filter tray.

### 8.9 Mobile layout

Use a top search field, horizontally scrollable quick filters, and a full-screen filter sheet for advanced narrowing.

### 8.10 Important states

* fresh search
* filtered results
* zero matches
* AI query interpretation available
* AI unavailable, literal search only

### 8.11 Accessibility and usability notes

* Search input must be reachable quickly by keyboard and touch.
* Active filters must be visible in text, not implied only by control state.
* No-results states should suggest the next useful action.

### 8.12 Notes for kitchen-readability where relevant

Not kitchen-focused.

---

## 9. Recipe Detail

### 9.1 Screen purpose

Recipe Detail is the dossier screen. It presents the full recipe, trust context, source context, and editing pathways in one structured page.

### 9.2 Primary tasks

* understand the recipe quickly
* inspect ingredients, steps, notes, and source
* assess trust and provenance
* enter Kitchen Mode
* edit or refine the recipe

### 9.3 Must be visible immediately on open

When a user opens a recipe, the screen must immediately show:

* recipe title
* verification or trust state
* key metadata strip
* ingredients entry point
* method entry point
* Kitchen Mode action
* source/provenance access

The screen should answer, within the first viewport:

* what this recipe is
* whether it is trusted
* what the user needs
* what the next action is

### 9.4 Information hierarchy

1. Title and core actions
2. Metadata strip
3. Ingredients
4. Method
5. Notes and service guidance
6. Source and trust panel
7. Optional revision or related information

### 9.5 Required components

* Page header with title
* Status chips
* Metadata strip
* Ingredient list module
* Method/steps module
* Notes panel
* Source/provenance panel
* Primary action buttons
* Optional AI action entry points

### 9.6 Primary actions

* enter Kitchen Mode
* edit recipe
* mark favorite
* change verification state if allowed in this view

### 9.7 Secondary actions

* open source URL where relevant
* archive/unarchive
* request AI suggestions
* export recipe

### 9.8 Desktop layout

Use a dossier layout with strong sectional rhythm:

* left main column for ingredients and steps
* right metadata/source rail
* top header spanning full content width

Recommended order:

* header
* metadata strip
* two-column body

The right rail should hold trust, source, timing, and operational metadata. It should not overpower the method content.

### 9.9 Tablet layout

Keep header and metadata full width. Collapse the right rail into stacked sections below ingredients and method or into an accordion-style support panel.

### 9.10 Mobile layout

Use a single-column vertical order:

* title
* action row
* status and metadata
* ingredients
* method
* notes
* source and trust

Ingredients and method must remain immediately accessible without deep tabbing.

### 9.11 Important states

* verified recipe
* draft or unverified recipe
* archived recipe
* missing source details
* optional AI suggestion available state

### 9.12 Accessibility and usability notes

* Headings must create a clear screen-reader outline.
* Ingredients and steps must be structured as lists.
* Action labels must be explicit, especially for trust-state changes.
* Source and trust panels must be readable without hover behavior.

### 9.13 Notes for kitchen-readability where relevant

The Recipe Detail screen is not Kitchen Mode, but it should still keep ingredients and steps highly legible and avoid crowded metadata blocks.

---

## 10. Kitchen Mode

### 10.1 Screen purpose

Kitchen Mode is the reduced-use screen for active cooking. It strips away archive density and prioritizes large, stable, touch-friendly reading.

### 10.2 Primary tasks

* read ingredients at arm’s length
* follow steps in sequence
* keep place while cooking
* stay oriented without reopening the full recipe layout

### 10.3 Information hierarchy

1. Recipe title
2. Current step or step list
3. Ingredient access
4. Minimal utility metadata
5. Large navigation controls

### 10.4 Required components

* Kitchen header
* Step display or step list
* Ingredient panel or slide-up sheet
* Previous/next step controls
* Step progress indicator
* Exit to Recipe Detail control
* Optional keep-awake notice or preference hint

### 10.5 Primary actions

* next step
* previous step
* open ingredient list
* exit Kitchen Mode

### 10.6 Secondary actions

* jump to a specific step
* toggle full ingredient view
* mark recipe as cooked

### 10.7 Desktop layout

Use a focused centered column with generous spacing and minimal side content.

Recommended structure:

* compact top bar
* large primary step area
* optional side ingredient panel if screen width allows

### 10.8 Tablet layout

This is the most important Kitchen Mode target.

Use:

* large central step area
* persistent bottom navigation controls
* slide-over ingredient panel or split view depending on orientation

### 10.9 Mobile layout

Use a single-column reading layout with:

* large step text
* fixed bottom previous/next controls
* ingredient sheet or full-screen ingredient overlay

Avoid small tabs, dense accordions, or tiny inline metadata in this mode.

### 10.10 Important states

* step-by-step mode
* full method mode
* ingredients open
* landscape tablet mode
* low-content recipe with only a few steps

### 10.11 Accessibility and usability notes

* Text must remain legible at arm’s length.
* Controls must support large tap targets.
* High contrast is mandatory.
* Step progress must be communicated with text and structure, not only color or thin indicators.

### 10.12 Notes for kitchen-readability where relevant

This screen has the strictest readability requirement in the product:

* larger type
* increased spacing
* reduced chrome
* stable control positions
* minimal distractions

---

## 11. Intake / Import Hub

### 11.1 Screen purpose

The Intake Hub is the controlled gateway into the archive. It helps the user choose the right intake path and reopen unfinished intake jobs.

### 11.2 Primary tasks

* choose an intake method
* understand the difference between intake types
* reopen in-progress or failed intake jobs
* move into manual, text, URL, or file intake

### 11.3 Information hierarchy

1. Intake heading and short framing
2. Intake path choices
3. In-progress review queue
4. Recent intake jobs
5. Optional guidance notes

### 11.4 Required components

* Page header
* Intake type cards or rows
* Intake queue list
* Status chips
* Recent job list
* Empty state for no jobs

### 11.5 Primary actions

* start manual entry
* start paste text intake
* start URL intake
* start file intake
* resume intake review

### 11.6 Secondary actions

* inspect failed jobs
* filter queue by status
* remove abandoned intake jobs if supported

### 11.7 Desktop layout

Use:

* top heading and explanation
* first row of intake path cards
* lower section for active queue and recent jobs

Queue content should feel operational, not promotional.

### 11.8 Tablet layout

Keep intake choices in a two-column grid where space allows. Move queue and recent items into stacked panels below.

### 11.9 Mobile layout

Use stacked intake cards followed by a simplified queue list. Avoid dense table-style job lists on mobile.

### 11.10 Important states

* no active intake jobs
* active review queue
* failed intake job present
* AI unavailable note shown where relevant

### 11.11 Accessibility and usability notes

* Intake path labels must be explicit and not rely on icon meaning alone.
* Queue state must be understandable from text labels and timestamps.
* Resume actions must be easy to distinguish from starting a new intake.

### 11.12 Notes for kitchen-readability where relevant

Not kitchen-relevant.

---

## 12. Paste Text Intake

### 12.1 Screen purpose

Paste Text Intake is the fast capture surface for messy source material copied from web pages, notes, messages, or documents.

### 12.2 Primary tasks

* paste raw recipe text
* preserve that source
* choose whether to normalize manually or with AI
* continue into review

### 12.3 Information hierarchy

1. Intake heading and source framing
2. Raw source input
3. Source metadata fields
4. Normalize actions
5. Save-progress guidance

### 12.4 Required components

* Page header
* Large multiline source field
* Source notes field
* Optional source title field
* AI availability status
* Primary action bar
* Inline guidance and validation messages

### 12.5 Primary actions

* normalize with AI
* continue manually
* save intake draft

### 12.6 Secondary actions

* clear input
* paste from clipboard if browser permissions allow
* open AI settings if unavailable

### 12.7 Desktop layout

Use a split emphasis layout:

* dominant left pane for raw text input
* narrower right pane for source metadata, AI status, and action stack

This keeps the source visually primary.

### 12.8 Tablet layout

Use a stacked layout with:

* full-width source field
* secondary metadata/action panel beneath or beside it depending on orientation

### 12.9 Mobile layout

Use a single-column layout:

* large source field first
* metadata fields next
* fixed or sticky action bar at bottom if practical

### 12.10 Important states

* empty input
* valid source pasted
* AI connected
* AI unavailable
* validation error
* saved draft

### 12.11 Accessibility and usability notes

* The raw text field must have strong visible focus and clear labeling.
* AI status must not rely on color alone.
* Primary actions must remain accessible without excessive scrolling after large paste operations.

### 12.12 Notes for kitchen-readability where relevant

Not kitchen-relevant.

---

## 13. Intake Review / Normalize

### 13.1 Screen purpose

This is the trust gate for non-manual intake. It presents raw source beside structured candidate output so the user can review, edit, and approve deliberately.

### 13.2 Primary tasks

* compare raw source to structured candidate
* review AI-suggested or parsed fields
* edit incorrect values
* accept or reject field-level suggestions
* save as Draft, Unverified, or Verified

### 13.3 Information hierarchy

1. Review status and trust framing
2. Raw source panel
3. Structured candidate panel
4. Field-level review actions
5. Final save/trust action area

### 13.4 Required components

* Review header
* Raw source panel
* Structured candidate editor
* AI result panel styling where relevant
* Status chips
* Field-level review controls
* Save/approve action bar
* Inline error or partial-result messaging

### 13.5 Primary actions

* accept field
* edit field
* reject field
* save as Draft
* save as Unverified
* save as Verified

### 13.6 Secondary actions

* reject all AI suggestions
* retry normalization
* return to intake source
* save and resume later

### 13.7 Desktop layout

Use a strong side-by-side review layout:

* left pane for raw source
* right pane for structured candidate editor
* persistent lower or upper action bar for save and review actions

The side-by-side comparison is the preferred desktop pattern.

### 13.8 Tablet layout

Use either:

* split view in landscape
* stacked source then candidate in portrait

Review actions should remain visible without forcing the user to lose context between source and candidate.

### 13.9 Mobile layout

Use a segmented stacked review layout:

* source preview section
* candidate fields section
* sticky action bar for save and trust choice

Source and candidate must remain clearly distinguished even when stacked vertically.

### 13.10 Important states

* deterministic parse result
* AI-generated candidate
* partial candidate
* AI unavailable
* malformed or failed normalization
* saved partial review

### 13.11 Accessibility and usability notes

* Raw source and candidate sections must have distinct headings and landmarks.
* Suggested versus accepted versus manual fields must not be distinguished by color alone.
* Save actions must clearly state trust consequences.
* Partial review state must be recoverable and clearly indicated.

### 13.12 Notes for kitchen-readability where relevant

Not kitchen-focused, but candidate steps and ingredients should still be clearly readable and editable without cramped form density.

---

## 14. Settings

### 14.1 Screen purpose

Settings provides configuration for archive behavior, UI preferences, import defaults, kitchen preferences, AI settings, and backup/export management.

### 14.2 Primary tasks

* change archive defaults
* manage import behavior
* configure AI connection
* adjust kitchen and UI preferences
* run backup or export actions

### 14.3 Information hierarchy

1. Settings section navigation
2. Active settings panel
3. Save and feedback area
4. Diagnostics or status information where relevant

### 14.4 Required components

* Settings navigation list
* Section panels
* Form fields
* Save state indicators
* AI availability status in the AI section
* Backup/export controls

### 14.5 Primary actions

* save settings changes
* test AI connection
* configure model roles
* create backup

### 14.6 Secondary actions

* reset a section to defaults if supported
* inspect backup metadata
* open storage path information

### 14.7 Desktop layout

Use a left settings section rail and a right content panel.

The AI settings section should show:

* enable/disable control
* endpoint
* model role mapping
* connection test result

### 14.8 Tablet layout

Use a collapsible settings section list with a single active content panel.

### 14.9 Mobile layout

Use a section list landing page or top segmented navigation into single-column forms. Avoid showing all settings groups in one long unstructured page.

### 14.10 Important states

* clean saved state
* unsaved changes
* validation error
* AI connected
* AI unavailable
* backup in progress

### 14.11 Accessibility and usability notes

* Form labels must be explicit and persistent.
* Save states must be visible in text, not only icon treatment.
* Diagnostics should remain understandable to non-technical home users.

### 14.12 Notes for kitchen-readability where relevant

Kitchen settings should preview their effects in plain language, especially text size and step display preferences.

---

## 15. AI Tools Surface / AI Action Layer

### 15.1 Screen purpose

The AI Tools surface gathers optional AI workflows without turning AI into the main product identity. It also defines how AI actions appear inside other archive screens.

### 15.2 Primary tasks

* start a normalization workflow
* request metadata suggestions
* request rewrite proposals
* run pantry-based suggestion workflows
* inspect AI availability before starting work

### 15.3 Information hierarchy

1. AI tools heading with optional framing
2. AI availability and configuration state
3. Task cards or task modules
4. Recent AI jobs or last results where useful
5. Entry points back to archive contexts

### 15.4 Required components

* AI availability status
* AI action buttons
* Tool cards or modules
* AI result panel pattern
* Link to AI settings

### 15.5 Primary actions

* normalize recipe
* suggest metadata
* rewrite recipe
* cook from ingredients

### 15.6 Secondary actions

* view AI settings
* inspect recent AI jobs
* dismiss unavailable state

### 15.7 Desktop layout

Use a restrained task grid or modular stack.

The AI availability panel should sit above the tools, not dominate the entire page. Tool cards should feel subordinate to archive maintenance work rather than like a chat dashboard.

### 15.8 Tablet layout

Use a two-column card layout or stacked modules depending on width. Keep recent AI job history secondary.

### 15.9 Mobile layout

Use stacked tool rows or cards with status at top and clear CTA labels. Avoid conversational composer patterns.

### 15.10 Important states

* AI connected
* AI not configured
* AI unavailable
* AI processing
* AI result ready

### 15.11 Accessibility and usability notes

* AI actions must be explicitly labeled as optional.
* AI result states must be textually clear.
* Availability indicators must not rely on color only.

### 15.12 Notes for kitchen-readability where relevant

Pantry and suggestion outputs should remain readable on tablet and mobile, but this is not a kitchen-mode screen.

### 15.13 Embedded AI action layer rules

On other screens, AI actions should appear as subordinate controls:

* Intake screens: normalize or assist actions near structured review work
* Recipe Detail: suggest metadata or rewrite actions in a secondary action zone
* Search: natural-language interpretation only as a supplement to direct search

AI controls must never visually outrank the primary archive actions on those screens.

---

## 16. Cross-screen consistency rules

### Established facts

The product must feel like one calm operational system.

### Consistency rules

* Primary navigation placement should remain stable across major screens.
* Status chips should use the same language and hierarchy everywhere.
* Trust state labels must remain consistent across library, recipe detail, and intake review.
* AI suggestion styling must remain visually distinct from approved data.
* Source/provenance modules should follow a consistent structure.
* Page headings should lead with archive context, not decorative naming.
* Action hierarchy should stay predictable: primary archive action first, optional AI action second.

---

## 17. Navigation transition notes

### Transition rules

* Library to Recipe Detail should feel immediate and context-preserving.
* Recipe Detail to Kitchen Mode should feel like entering a focused operational state, not a different product.
* Intake Hub to intake-specific screens should preserve the selected intake type context clearly.
* Paste Text Intake to Intake Review should preserve raw source continuity.
* AI tool actions that launch recipe or intake workflows should land inside the same review architecture used elsewhere.
* Settings changes that affect AI or Kitchen Mode should return the user to those areas without ambiguity where appropriate.

### Recommendation

Unsaved intake review and edit states should always warn before destructive navigation away from the screen.

---

## 18. MVP screen priorities

### Priority 1

* Library
* Recipe Detail
* Kitchen Mode
* Intake Hub
* Paste Text Intake
* Intake Review / Normalize

These define the archive core.

### Priority 2

* Settings
* AI Tools surface

These are necessary for configuration and optional AI use, but they should not delay core archive use.

### Priority rule

If implementation sequencing forces tradeoffs, complete the archive, intake, and kitchen-reading screens before expanding the standalone AI surface.

---

## Decisions made

1. The v1 screen set includes Library, Recipe Detail, Kitchen Mode, Intake Hub, Paste Text Intake, Intake Review / Normalize, Settings, and an AI Tools surface plus embedded AI action rules.
2. Library is the command-center screen and Recipe Detail is the dossier screen.
3. Kitchen Mode is a reduced, highly legible task state rather than a general browsing surface.
4. Intake Review / Normalize is the trust gate and uses a strong source-versus-candidate comparison structure.
5. AI tools remain subordinate to archive workflows and must not visually outrank primary archive actions.
6. Responsive behavior favors stacked clarity on mobile and side-by-side comparison on desktop where review requires it.

## Open questions

1. Should the Library default to list rows or compact cards on desktop in the first build?
2. Should Kitchen Mode default to step-by-step view or full-method view on first open?
3. Should the AI Tools surface include recent AI job history in v1, or should job history remain visible only in context-specific screens?
4. How much source preview should mobile Intake Review show before collapsing the raw source into an expandable section?

## Deliverables created

1. `/docs/02_ux/screen-blueprint-pack.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how the local-first product is installed, run, configured, and accessed on a single machine and optionally across a home local network.

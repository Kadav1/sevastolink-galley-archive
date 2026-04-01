# Sevastolink Galley Archive

## Information Architecture Spec v1.0

---

1. Purpose

This document defines the information architecture for Sevastolink Galley Archive.

Its job is to establish:
	•	the structure of the product
	•	how screens relate to one another
	•	how users move through the archive
	•	what information belongs where
	•	what the primary flows are
	•	how the system should scale without becoming messy

This is the target-state structural backbone of the product.

Current implementation note:

* this document describes the intended information architecture
* it does not describe the narrower current route set shipped in the app today
* use `docs/02_ux/implemented-routes-and-flows.md` for the implementation-aware route baseline

---

## Current-state gap note

The current frontend does not yet implement most of the route and navigation expansion described below.

Implemented today:

* library landing and browse
* recipe detail
* kitchen mode
* intake hub
* manual entry
* paste-text intake
* settings placeholder

Not yet implemented today:

* library sub-routes such as favorites, recent, verified, drafts, and search results
* AI tools routes
* URL import and file intake routes
* recipe edit route
* settings sub-pages

The remainder of this document should be read as target-state IA, not as a description of the current app.

⸻

2. IA Philosophy

Sevastolink Galley Archive should be structured as a local operational archive, not as a content feed.

The architecture should optimize for four things:

2.1 Retrieval

The user must be able to find recipes quickly by:
	•	title
	•	ingredient
	•	cuisine
	•	dish role
	•	time
	•	complexity
	•	status
	•	tags/facets

2.2 Use

Once opened, a recipe must be immediately usable:
	•	readable
	•	structured
	•	stable
	•	easy to act on in the kitchen

2.3 Intake

The system must make it easy to bring new material into the archive without compromising structure.

2.4 Preservation

Recipes should not feel disposable. The architecture should support:
	•	refinement
	•	notes
	•	trust/verification
	•	source tracking
	•	revisions
	•	long-term archive value

Storage-aware decision support should be treated as a supporting retrieval and preservation aid rather than as a separate top-level product priority. It should help the user answer:
	•	what should be used soon
	•	which archive records fit current pantry or fridge conditions
	•	how storage-aware metadata should inform retrieval without replacing archive judgment

This support should remain subordinate to the archive rather than becoming a separate grocery or inventory product.

⸻

3. Product Structure Model

At the highest level, the product is made of six functional zones:

3.1 Archive

The main recipe library and browsing/search space.

3.2 Recipe View

The detailed page for a single recipe.

3.3 Kitchen Use

A focused mode for active cooking.

3.4 Intake

All flows for adding, normalizing, and structuring recipes.

3.5 Intelligence Layer

Optional AI-assisted tools for structuring, enrichment, and retrieval.

Storage-aware guidance and pantry-driven decision support should live inside archive and retrieval flows, optionally assisted by this layer. They should not become a separate top-level product zone.

3.6 System / Settings

Configuration, preferences, storage, AI connection, and archive maintenance.

⸻

4. Primary App Map

The top-level map should look like this:

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
├── Intake
│   ├── Manual Entry
│   ├── Paste Text
│   ├── URL Import
│   ├── Image / PDF Intake
│   └── Normalize / Review
├── AI Tools
│   ├── Normalize Recipe
│   ├── Suggest Metadata
│   ├── Rewrite Recipe
│   ├── Compare Similar
│   └── Ingredient Retrieval Assist
└── Settings
    ├── Archive Settings
    ├── UI Preferences
    ├── Kitchen Mode Preferences
    ├── Import Settings
    ├── LM Studio / AI Settings
    └── Backup / Export


⸻

5. Navigation Model

5.1 Primary navigation

The app should have a stable primary navigation with these top-level entries:
	•	Library
	•	Intake
	•	AI Tools
	•	Settings

Recipe Detail and Kitchen Mode should not feel like separate “apps.”
They should feel like focused states within the archive system.

5.2 Recipe access

Recipes should be reachable from:
	•	library results
	•	favorites
	•	recent
	•	filtered lists
	•	related recipe suggestions
	•	AI results where relevant

5.3 Kitchen Mode access

Kitchen Mode should be reachable only from:
	•	an open recipe
	•	optionally a “resume last used recipe” shortcut later

Kitchen Mode is not a browse space. It is a task state.

5.4 Search behavior

Search should be globally accessible from the library shell.

Search should support:
	•	direct text search
	•	filtered search
	•	faceted narrowing
	•	later semantic search

⸻

6. Recommended Route Structure

Suggested route model:

/                       → redirect to /library
/library                → archive default view
/library/favorites      → favorite recipes
/library/recent         → recently viewed/used
/library/verified       → trusted recipes
/library/drafts         → unverified/draft recipes
/library/search         → text/facet search results
/recipe/:slug           → main recipe detail
/recipe/:slug/kitchen   → kitchen mode
/recipe/:slug/edit      → edit recipe
/intake                 → intake hub
/intake/manual          → manual creation
/intake/paste           → paste raw text
/intake/url             → URL import
/intake/file            → image/PDF import
/intake/review/:id      → review normalized intake result
/ai                     → AI tools landing
/ai/normalize           → normalize recipe flow
/ai/rewrite             → rewrite recipe flow
/ai/suggest-metadata    → metadata enrichment flow
/ai/pantry              → optional AI-assisted ingredient retrieval entry
/settings               → settings landing
/settings/archive       → archive/storage settings
/settings/ui            → UI preferences
/settings/kitchen       → kitchen mode settings
/settings/import        → intake/import preferences
/settings/ai            → LM Studio integration settings
/settings/export        → backup/export/settings

This structure keeps the product understandable and leaves room for expansion.

Target-state note:

* Library retrieval modes and the existing ingredient-first flow may later surface use-soon contexts
* leftovers and preservation-oriented retrieval may appear as archive-connected browse states
* storage-reference support may be linked from recipe detail and ingredient-first retrieval surfaces

These should be treated as archive-connected retrieval aids, not as a separate app within the product.

⸻

7. Screen Hierarchy

7.1 Library

This is the command center.

Primary purpose
	•	browse
	•	search
	•	filter
	•	locate
	•	enter recipes quickly

Primary content
	•	search
	•	filters
	•	recipe cards/list rows
	•	favorites/recent/trust indicators

Secondary content
	•	quick metadata
	•	archive summaries
	•	optional counts
	•	optional recently added or revised items

⸻

7.2 Recipe Detail

This is the dossier page.

Primary purpose
	•	understand the recipe fully
	•	trust the recipe
	•	act on the recipe
	•	refine the recipe

Primary content hierarchy
	1.	Title
	2.	Metadata strip
	3.	Ingredients
	4.	Method
	5.	Service notes
	6.	Source/status
	7.	Revision/history

Secondary content
	•	image
	•	related recipes
	•	AI suggestions
	•	archival metadata

⸻

7.3 Kitchen Mode

This is an execution state.

Primary purpose
	•	active cooking use

Primary content
	•	title
	•	servings
	•	time
	•	ingredients
	•	active steps
	•	service reminders

Secondary content
	•	image
	•	source
	•	secondary metadata
	•	archive links

Kitchen Mode should aggressively suppress non-essential information.

⸻

7.4 Intake Hub

This is the archive control gate.

Primary purpose
	•	add new recipes cleanly
	•	choose correct intake path

Primary content
	•	intake options
	•	recent intake items
	•	unreviewed normalization jobs
	•	trust status / verification reminders

Intake branches
	•	Manual Entry
	•	Paste Text
	•	URL Import
	•	File/Image/PDF Intake

⸻

7.5 AI Tools

This is a tools layer, not the main navigation identity of the product.

Primary purpose
	•	enhance archive quality
	•	enhance retrieval
	•	reduce manual cleanup

Primary tools
	•	normalize recipe
	•	suggest metadata
	•	rewrite into archive style
	•	compare recipes
	•	pantry suggestion

AI tools should always feel subordinate to the archive.
Ingredient-driven AI assistance should hand the user back into archive retrieval rather than behaving like a separate pantry product.

⸻

7.6 Settings

This should be practical and small.

Primary purpose
	•	configure local behavior
	•	manage storage and archive preferences
	•	manage LM Studio connection
	•	manage presentation and kitchen mode preferences

Settings should not grow into a product section larger than the archive itself.

⸻

8. Primary User Flows

8.1 Find and cook a known recipe

Flow:
	1.	Open Library
	2.	Search title or use favorites/recent
	3.	Open Recipe Detail
	4.	Review metadata/ingredients
	5.	Enter Kitchen Mode
	6.	Cook

This is one of the most important flows and must be extremely smooth.

⸻

8.2 Discover something based on ingredients

Flow:
	1.	Open Library
	2.	Search/filter by ingredient families or pantry input
	3.	Review matching recipes
	4.	Open candidate recipes
	5.	Choose one
	6.	Cook or save to favorites

Later semantic/AI support can enrich this, but the structured system should support it already.
Optional AI-assisted ingredient retrieval may exist as a secondary helper entry, but the archive should remain the primary discovery surface.

The same flow may later include use-soon and leftovers-aware framing, but it should still feel like archive retrieval rather than recommendation-feed behavior.

⸻

8.3 Add a new recipe manually

Flow:
	1.	Open Intake
	2.	Choose Manual Entry
	3.	Fill structured fields
	4.	Save as draft or verified recipe
	5.	Review in Recipe Detail
	6.	Edit if needed

⸻

8.4 Convert messy text into a structured recipe

Flow:
	1.	Open Intake
	2.	Paste raw text
	3.	Run Normalize
	4.	Review extracted structure
	5.	Correct fields manually
	6.	Save as draft or verified recipe

This is the most important AI-assisted intake flow.

⸻

8.5 Import from URL or file

Flow:
	1.	Open Intake
	2.	Choose URL or File
	3.	Submit source
	4.	Process locally / AI-assisted where available
	5.	Review result
	6.	Save to archive

This flow should never bypass human review.

⸻

8.6 Refine an existing recipe

Flow:
	1.	Open Recipe Detail
	2.	Edit recipe
	3.	Update notes/service/source/revisions
	4.	Save
	5.	Mark verified if trusted

This flow is essential because the product is an evolving archive, not just a viewer.

⸻

9. Information Priorities by Screen

Library

Must be immediately visible
	•	search
	•	core filters
	•	recipe title
	•	key metadata
	•	favorite/verified state

Can be secondary
	•	images
	•	extended notes
	•	source details
	•	revision details

Recipe Detail

Must be immediately visible
	•	title
	•	timing
	•	servings
	•	ingredients
	•	method

Can be secondary
	•	image
	•	detailed source
	•	revision logs
	•	AI-derived support panels

Kitchen Mode

Must be immediately visible
	•	ingredients
	•	steps
	•	servings
	•	active time information

Must be suppressed
	•	archive clutter
	•	broad metadata
	•	source bureaucracy
	•	too many secondary actions

Intake

Must be immediately visible
	•	current input type
	•	raw source
	•	structured output
	•	review actions
	•	verification state

⸻

10. Search & Filter Architecture

The search model should be hybrid.

10.1 Direct search

Search by:
	•	title
	•	ingredient names
	•	cuisine
	•	tags
	•	notes
	•	source text where relevant

10.2 Faceted filtering

Filter by:
	•	dish role
	•	cuisine/tradition
	•	technique family
	•	ingredient family
	•	complexity
	•	time class
	•	service format
	•	season/mood
	•	dietary flags
	•	storage profile
	•	verified/favorite state

10.3 Future semantic search

Later, AI/embeddings can support:
	•	similar recipes
	•	pantry idea search
	•	fuzzy conceptual retrieval

But semantic search must remain an enhancement, not the only discovery system.

⸻

11. Archive Object Model

At an IA level, the key object is the Recipe.

Related supporting objects/states:
	•	Tag / Facet
	•	Source
	•	Revision
	•	Media Asset
	•	Intake Job
	•	AI Processing Result
	•	Verification State
	•	Favorite State

The archive should be centered on the recipe, not on tags, collections, or social constructs.

⸻

12. Verification & Trust Model

Recipes should have a trust state that is visible in the information architecture.

Suggested states:
	•	Draft
	•	Unverified
	•	Verified
	•	Archived

This matters because the product is an archive, not just a display layer.

IA implication

The Library should support:
	•	viewing drafts separately
	•	viewing trusted recipes separately
	•	filtering by verification state
	•	intake review queues

⸻

13. Content Relationship Model

A recipe can have:
	•	one title
	•	one primary dish role
	•	one primary cuisine
	•	optional secondary cuisines
	•	many ingredient families
	•	many tags/facets
	•	one or more source references
	•	one or more media assets
	•	one current version
	•	optional revision history
	•	optional AI processing records

This model supports complexity without making the UI feel like a database admin tool.

⸻

14. Responsive IA Rules

Desktop

Can support:
	•	library + detail split thinking
	•	side filters
	•	optional side metadata panel
	•	deeper archive navigation

Tablet

Should prioritize:
	•	recipe reading
	•	kitchen use
	•	simplified but roomy library browsing

Mobile

Should prioritize:
	•	search
	•	favorites/recent
	•	quick open
	•	kitchen mode
	•	low-friction reading

The structure should remain the same across devices, but the presentation density should change.

⸻

15. Settings IA

Settings should be divided into practical groups:

Archive
	•	archive defaults
	•	verification defaults
	•	backup/export

UI
	•	density
	•	image preferences
	•	theme preferences if relevant

Kitchen Mode
	•	large text options
	•	step display preferences
	•	keep screen awake behavior if applicable through browser/device guidance

Intake
	•	intake defaults
	•	review preferences
	•	source handling

AI / LM Studio
	•	enable/disable AI features
	•	endpoint settings
	•	model role mapping
	•	fallback behavior

⸻

16. Expansion Strategy

The architecture should be able to grow without breaking.

Safe later expansions
	•	storage-aware retrieval refinements
	•	semantic search
	•	OCR/file processing
	•	recipe comparison
	•	version history improvements

Things that should not distort the IA
	•	social features
	•	public feed models
	•	content discovery feed behaviors
	•	chat-first AI layer

The archive must remain the center of gravity.

⸻

17. IA Success Criteria

The information architecture succeeds if:
	•	the user can find a recipe quickly
	•	the user can move from archive to cooking with low friction
	•	intake is controlled and trustworthy
	•	AI features feel optional and useful
	•	the structure scales without becoming messy
	•	the archive feels like a long-term system, not a temporary tool

⸻

18. Final IA Standard

Any structural decision should be judged by this question:

Does this make the archive easier to retrieve from, cook from, and maintain over time?

If not, it does not belong in the architecture.

⸻

Recommended next foundation document

The next document should be:

Component Inventory & Behavior Spec

That document should define:
	•	all core components
	•	variants
	•	states
	•	interactions
	•	dependencies
	•	usage rules across screens

⸻

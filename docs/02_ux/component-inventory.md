Sevastolink Galley Archive

Component Inventory & Behavior Spec v1.0

1. Purpose

This document defines the core component system for Sevastolink Galley Archive.

It establishes:
	•	what components exist
	•	what each component is for
	•	where each component is used
	•	what states and variants each component needs
	•	how components should behave
	•	how they should scale across desktop, tablet, mobile, and kitchen mode

This is the component-level source of truth for design and implementation.

⸻

2. Component Philosophy

The component system should feel:
	•	structured
	•	restrained
	•	modular
	•	readable
	•	durable
	•	operational

Every component should serve one of three purposes:
	•	navigation
	•	archive comprehension
	•	action

A component should never exist only for visual flavor.

⸻

3. Component Categories

The system should be organized into these component groups:
	1.	Application Shell
	2.	Navigation Components
	3.	Search & Filter Components
	4.	Archive Browsing Components
	5.	Recipe Content Components
	6.	Intake & Import Components
	7.	AI Interaction Components
	8.	Status & Metadata Components
	9.	Form & Input Components
	10.	Feedback & Overlay Components
	11.	Kitchen Mode Components
	12.	Utility Components

⸻

4. Application Shell Components

4.1 App Shell

Purpose

Defines the main product frame.

Contains
	•	left rail or filter/navigation zone
	•	top search/action zone
	•	main content pane
	•	optional right context pane on desktop

States
	•	default
	•	compact
	•	recipe detail context
	•	intake context
	•	kitchen mode suppressed shell

Rules
	•	must remain stable across the app
	•	should not visually dominate content
	•	should provide predictable placement for search and navigation

⸻

4.2 Content Frame

Purpose

Wraps the main page content.

Used in
	•	Library
	•	Recipe Detail
	•	Intake
	•	Settings
	•	AI tool panels

Variants
	•	standard
	•	wide
	•	split-pane
	•	focus mode

Behavior
	•	adjusts spacing and max width by screen type
	•	maintains consistent top/bottom rhythm

⸻

5. Navigation Components

5.1 Primary Nav Rail

Purpose

Top-level movement between product zones.

Items
	•	Library
	•	Intake
	•	AI Tools
	•	Settings

States
	•	default
	•	active
	•	hover
	•	collapsed
	•	mobile drawer

Rules
	•	active state must be unmistakable
	•	labels should stay readable
	•	icons may support, not replace, labels

⸻

5.2 Section Header

Purpose

Marks major page sections and local context.

Used in
	•	Library sections
	•	Recipe sections
	•	Intake steps
	•	Settings groups

Variants
	•	page-level
	•	module-level
	•	inline section divider

⸻

5.3 Breadcrumb / Context Trail

Purpose

Shows where the user is within archive or intake flow.

Used in
	•	Intake review
	•	nested settings
	•	recipe edit flows if needed

Rules
	•	must remain minimal
	•	should not appear everywhere by default

⸻

6. Search & Filter Components

6.1 Global Search Bar

Purpose

Primary archive retrieval control.

Used in
	•	Library
	•	search results
	•	optionally header shell

States
	•	idle
	•	focused
	•	active query
	•	loading
	•	no results

Behavior
	•	supports text input
	•	can trigger filters
	•	should feel fast and central

⸻

6.2 Filter Group

Purpose

Groups related taxonomy filters.

Used for
	•	role
	•	cuisine
	•	technique
	•	time
	•	complexity
	•	storage
	•	dietary
	•	verification

Variants
	•	expanded
	•	collapsed
	•	inline
	•	drawer/mobile

Rules
	•	each group must be scannable
	•	not all groups should be fully expanded at once on smaller screens

⸻

6.3 Filter Option

Purpose

Represents one filterable value.

Variants
	•	checkbox-style multi-select
	•	radio-style single-select
	•	chip-style quick toggle

States
	•	default
	•	selected
	•	disabled
	•	hover
	•	unavailable/zero-result

⸻

6.4 Active Filter Bar

Purpose

Shows currently applied filters.

Contains
	•	active tags
	•	clear all
	•	remove single filter

Rules
	•	should remain compact
	•	should not become visually noisy

⸻

7. Archive Browsing Components

7.1 Recipe Card

Purpose

Primary archive browsing unit.

Contains
	•	title
	•	primary metadata
	•	optional image
	•	favorite state
	•	verification state
	•	compact descriptors

Variants
	•	list row
	•	compact card
	•	image-forward card
	•	dense archive row

States
	•	default
	•	hover
	•	selected
	•	favorite
	•	verified
	•	draft/unverified

Rules
	•	title must dominate
	•	metadata ordering must be consistent
	•	images must never overwhelm retrieval usefulness

⸻

7.2 Recipe List Row

Purpose

Dense alternative to recipe cards.

Best for
	•	desktop browsing
	•	keyboard-heavy archive use
	•	larger archives

Contains
	•	title
	•	quick metadata columns
	•	favorite/status markers

Rules
	•	optimized for scan speed
	•	reduced visual weight compared to cards

⸻

7.3 Collection Strip

Purpose

Shows subsets like:
	•	Favorites
	•	Recent
	•	Verified
	•	Drafts

Variants
	•	horizontal rail
	•	grid section
	•	quick-access panel

⸻

7.4 Empty State

Purpose

Handles zero-results or empty collections.

Types
	•	no recipes yet
	•	no search matches
	•	no favorites
	•	no drafts
	•	no intake jobs

Rules
	•	should guide next action
	•	should not feel punitive

⸻

8. Recipe Content Components

8.1 Recipe Header

Purpose

Introduces a recipe clearly.

Contains
	•	title
	•	short descriptor
	•	primary actions
	•	optional hero image

Actions
	•	favorite
	•	edit
	•	kitchen mode
	•	print/export

⸻

8.2 Metadata Strip

Purpose

Compressed operational data band.

Typical fields
	•	role
	•	cuisine
	•	technique
	•	time
	•	yield
	•	complexity
	•	heat window
	•	verification state

Variants
	•	full
	•	compact
	•	kitchen-reduced

Rules
	•	same order everywhere
	•	not too many badges
	•	one of the main Sevastolink-defining components

⸻

8.3 Ingredient Section

Purpose

Displays ingredient manifest.

Variants
	•	standard list
	•	grouped list
	•	checklist-style kitchen mode variant

States
	•	default
	•	scaled servings
	•	substituted/edited
	•	highlighted

Rules
	•	quantities and units must scan cleanly
	•	ingredient text must remain more prominent than styling

⸻

8.4 Step / Method Section

Purpose

Displays recipe procedure.

Variants
	•	standard numbered steps
	•	compact steps
	•	kitchen focus steps
	•	step-by-step mode later

States
	•	default
	•	expanded notes
	•	active step
	•	completed step later if needed

Rules
	•	step order must be obvious
	•	steps need strong spacing and hierarchy

⸻

8.5 Service Notes Block

Purpose

Captures plating, storage, wine, substitutions, and “what I learned.”

Variants
	•	simple text block
	•	structured note group
	•	archive notes with labels

⸻

8.6 Source & Provenance Block

Purpose

Shows where a recipe came from and how trustworthy it is.

Contains
	•	source URL or source note
	•	imported/manual
	•	verified state
	•	revision status

⸻

8.7 Revision History Panel

Purpose

Tracks changes across time.

v1 scope
	•	simple last-updated and revision markers

later scope
	•	real version comparison
	•	change notes
	•	rollback support

⸻

9. Intake & Import Components

9.1 Intake Method Selector

Purpose

Lets user choose:
	•	Manual
	•	Paste Text
	•	URL
	•	File/Image/PDF

Rules
	•	should make the workflow obvious
	•	should reduce ambiguity at entry

⸻

9.2 Raw Input Panel

Purpose

Holds the incoming messy material.

Used for
	•	pasted recipe text
	•	OCR output
	•	imported source content

Rules
	•	always distinguish raw source from structured result

⸻

9.3 Structured Output Panel

Purpose

Shows normalized recipe fields before save.

Contains
	•	title
	•	taxonomy fields
	•	ingredients
	•	steps
	•	notes
	•	source

States
	•	generated
	•	edited
	•	approved
	•	partially incomplete

⸻

9.4 Review Comparison View

Purpose

Lets the user compare:
	•	raw source
	•	AI-structured result
	•	editable final archive form

Rules
	•	must support trust
	•	must keep human approval central

⸻

9.5 Verification Action Bar

Purpose

Lets user mark:
	•	save as draft
	•	save as unverified
	•	save as verified

⸻

10. AI Interaction Components

10.1 AI Action Button

Purpose

Triggers AI-assisted tasks.

Examples
	•	Normalize Recipe
	•	Suggest Metadata
	•	Rewrite in Archive Format
	•	Find Similar
	•	Pantry Suggestions

Rules
	•	should never overshadow core archive actions
	•	must clearly imply optional behavior

⸻

10.2 AI Result Panel

Purpose

Displays AI output.

Types
	•	normalized recipe
	•	metadata suggestions
	•	rewrite output
	•	similarity results
	•	pantry suggestions

States
	•	loading
	•	success
	•	partial
	•	unavailable
	•	failed

Rules
	•	must visually distinguish AI output from confirmed data

⸻

10.3 AI Availability Status

Purpose

Shows LM Studio connection state.

States
	•	connected
	•	unavailable
	•	processing
	•	degraded

Rules
	•	should be visible when relevant
	•	should not dominate normal browsing when unused

⸻

11. Status & Metadata Components

11.1 Status Chip

Purpose

Displays state markers like:
	•	Verified
	•	Draft
	•	Unverified
	•	Favorite
	•	Revised
	•	Archived

Rules
	•	compact
	•	consistent color logic
	•	no badge overload

⸻

11.2 Metadata Label/Value Pair

Purpose

Reusable micro-component for fields like:
	•	Yield: 4
	•	Time: 45 min
	•	Cuisine: Korean

Used in
	•	cards
	•	detail page
	•	kitchen mode
	•	AI panels

⸻

11.3 Tag / Facet Chip

Purpose

Displays taxonomy facets and filters.

States
	•	passive
	•	active
	•	removable
	•	disabled

⸻

12. Form & Input Components

12.1 Text Input

Uses
	•	title
	•	source
	•	notes
	•	search
	•	taxonomy free text

States
	•	idle
	•	focused
	•	filled
	•	error
	•	disabled

⸻

12.2 Text Area

Uses
	•	raw recipe input
	•	notes
	•	service notes
	•	method editing

Rules
	•	comfortable for long text
	•	visible labels required

⸻

12.3 Select / Multi-Select

Uses
	•	dish role
	•	cuisine
	•	technique
	•	ingredient families
	•	complexity
	•	storage
	•	dietary

Rules
	•	single-select for primary fields
	•	multi-select for facets only
	•	should remain usable on mobile

⸻

12.4 Toggle / Switch

Uses
	•	favorite
	•	verified behavior defaults
	•	AI enabled/disabled
	•	kitchen mode preferences

⸻

12.5 File Input / Upload Zone

Uses
	•	recipe image
	•	image import
	•	PDF import

States
	•	idle
	•	drag-ready
	•	uploading
	•	complete
	•	failed

⸻

13. Feedback & Overlay Components

13.1 Toast / Inline Confirmation

Purpose

Communicates:
	•	recipe saved
	•	metadata updated
	•	normalization complete
	•	AI unavailable
	•	import failed

Rules
	•	calm
	•	concise
	•	non-theatrical

⸻

13.2 Modal

Uses
	•	confirm destructive actions
	•	detailed review
	•	focused edit tasks
	•	import warning/validation issues

Rules
	•	only when necessary
	•	keep hierarchy strong
	•	don’t overuse

⸻

13.3 Drawer / Side Panel

Uses
	•	contextual metadata
	•	related recipes
	•	AI suggestions
	•	edit utilities on large screens

⸻

13.4 Skeleton / Loading State

Purpose

Shows loading without jarring shifts.

Used for
	•	library fetch
	•	recipe load
	•	AI processing
	•	import previews

⸻

14. Kitchen Mode Components

14.1 Kitchen Header

Contains
	•	recipe title
	•	yield
	•	time
	•	exit kitchen mode

Rules
	•	minimal
	•	stable
	•	always visible if useful

⸻

14.2 Kitchen Ingredient Block

Purpose

Readable ingredient manifest during cooking.

Variants
	•	full list
	•	grouped list
	•	checklist later

⸻

14.3 Kitchen Step Block

Purpose

Displays steps with strong separation.

Variants
	•	all steps visible
	•	focus step mode later

⸻

14.4 Kitchen Utility Strip

Purpose

Optional access to:
	•	timers
	•	notes
	•	scaling
	•	quick return to detail view

Rules
	•	secondary
	•	never clutter primary cooking content

⸻

15. Utility Components

15.1 Favorite Toggle

Purpose

Quickly mark/save recipes.

15.2 Print / Export Action

Purpose

Produce a clean printable view.

15.3 Share-to-local / Copy Action

Purpose

Copy recipe text or links locally.

15.4 Last Updated Marker

Purpose

Shows freshness and archival maintenance.

⸻

16. Component State Rules

Every major interactive component should define:

Visual states
	•	default
	•	hover
	•	active
	•	focus
	•	disabled
	•	loading
	•	error
	•	success where relevant

Data states
	•	empty
	•	partial
	•	complete
	•	draft
	•	verified
	•	archived

Responsive states
	•	desktop
	•	tablet
	•	mobile
	•	kitchen mode

No component should exist without explicit state behavior.

⸻

17. Component Dependency Rules

Some components depend on others:
	•	Recipe Card depends on Metadata Label/Value + Status Chip
	•	Recipe Detail depends on Recipe Header + Metadata Strip + Ingredient Section + Step Section
	•	Intake Review depends on Raw Input Panel + Structured Output Panel + Verification Action Bar
	•	Kitchen Mode depends on Recipe Header + Ingredient Block + Step Block
	•	AI panels depend on AI Availability Status + AI Result Panel + action triggers

This dependency model should guide component architecture in design and code.

⸻

18. MVP Component Set

The first build only needs a subset.

Must-have MVP components
	•	App Shell
	•	Primary Nav
	•	Global Search
	•	Filter Group
	•	Recipe Card
	•	Recipe Header
	•	Metadata Strip
	•	Ingredient Section
	•	Step Section
	•	Status Chip
	•	Text Input
	•	Text Area
	•	Select / Multi-Select
	•	Intake Method Selector
	•	Raw Input Panel
	•	Structured Output Panel
	•	AI Action Button
	•	AI Result Panel
	•	Toast
	•	Kitchen Header
	•	Kitchen Ingredient Block
	•	Kitchen Step Block

That is enough to build:
	•	Library
	•	Recipe Detail
	•	Kitchen Mode
	•	Intake / Normalize flow

⸻

19. Anti-Patterns

Do not allow the component system to drift into:
	•	badge spam
	•	dashboard card overload
	•	visual inconsistency between archive and kitchen mode
	•	AI panels that feel more important than recipes
	•	components that exist only to make the UI look “more Sevastolink”
	•	giant surface nesting with weak hierarchy

⸻

20. Final Component Standard

Every component should be judged by this question:

Does this component improve navigation, comprehension, or action inside the archive?

If not, it does not belong.

⸻

Recommended next foundation document

The next document should be:

Content & Taxonomy Spec

That should define:
	•	full field model
	•	enums
	•	tag/facet logic
	•	trust/verification model
	•	source model
	•	archival status model
	•	naming conventions for recipe records and metadata

⸻

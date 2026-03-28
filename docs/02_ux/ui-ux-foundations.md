# Sevastolink Galley Archive

## UI/UX Design Foundations v1.0

---

1. Purpose

This document establishes the UI/UX design language for Sevastolink Galley Archive.

It defines how the product should look, feel, behave, and communicate. Its purpose is to prevent drift and ensure that every screen, component, interaction, and future feature belongs to the same system.

This is not a generic recipe app.
This is not a literal terminal UI.
This is not cyberpunk or sci-fi cosplay.

Sevastolink Galley Archive should feel like a calm operational archive for domestic cooking:
	•	dark
	•	structured
	•	premium
	•	readable
	•	precise
	•	quiet
	•	reliable

Current implementation note:

* this document is a design-language reference, not a route or feature inventory
* its main value is visual and interaction direction rather than implementation completeness
* specific current route and feature availability should be taken from `docs/02_ux/implemented-routes-and-flows.md`

⸻

2. Product Experience Definition

Sevastolink Galley Archive is a local-first culinary command library.

The experience should feel like:
	•	a personal food archive
	•	a controlled domestic knowledge system
	•	a premium home utility
	•	an interface that supports cooking, retrieval, and refinement

The product should feel:
	•	intentional rather than decorative
	•	system-driven rather than trendy
	•	archival rather than social
	•	operational rather than playful

⸻

3. Core UX Principles

3.1 Structure over spectacle

Every screen should prioritize:
	•	clarity
	•	hierarchy
	•	retrieval
	•	legibility
	•	task flow

Visual identity should support utility, not overpower it.

3.2 Archive first

The system is primarily an archive, not a content feed.

The primary UX priorities are:
	•	finding a recipe
	•	understanding a recipe
	•	using a recipe
	•	improving a recipe
	•	preserving a recipe

3.3 Calm operational tone

The interface should feel controlled and quiet.

Avoid:
	•	excessive motion
	•	noisy gradients
	•	flashing indicators
	•	decorative clutter
	•	oversized labels or ornamental framing

3.4 Metadata is part of the design

Metadata is not secondary fluff.
Metadata is one of the key visual and functional layers of the product.

Time, yield, technique, cuisine, tags, status, source, and notes should be presented as a designed system.

3.5 Kitchen readability is mandatory

The product must work in practical cooking conditions:
	•	standing
	•	at arm’s length
	•	with partial attention
	•	with messy hands
	•	in varying light

3.6 Local-first trust

The UI should communicate:
	•	ownership
	•	privacy
	•	persistence
	•	reliability

Nothing should make the app feel disposable or cloud-dependent.

⸻

4. Sevastolink Design Translation

4.1 What Sevastolink means here

Sevastolink in this product means:
	•	restrained industrial hierarchy
	•	dark infrastructure aesthetics
	•	clear segmentation
	•	quiet status language
	•	premium system surfaces
	•	disciplined information rhythm

4.2 What Sevastolink does not mean here

It does not mean:
	•	terminal fonts everywhere
	•	fake shell prompts
	•	ASCII gimmicks
	•	glitch effects
	•	sci-fi props
	•	“hacker” styling
	•	excessive telemetry decoration

4.3 Correct translation

The right Sevastolink translation for this product is:
	•	dossier-like recipe pages
	•	metadata rails
	•	structured intake surfaces
	•	clear operational labels
	•	dark shell / bright content contrast
	•	quiet advisory accents

⸻

5. Visual Foundation

5.1 Color System

Core palette roles

Use semantic roles, not random colors.

Base surfaces
	•	Base Black — deepest background
	•	Graphite — main shell background
	•	Panel Black — cards, drawers, overlays
	•	Field Dark — inputs, embedded modules

Text
	•	Primary Text — soft white
	•	Secondary Text — muted pale grey
	•	Tertiary Text — dim metadata

Signal accents
	•	Signal Green — active, selected, confirmed, verified
	•	Amber — advisory, hover, emphasis, metadata activity
	•	Red — destructive, fault, warning only
	•	Blue-grey neutral — passive controls or cold secondary states if needed very sparingly

Color behavior rules
	•	Green is for active or trusted states
	•	Amber is for advisory emphasis, secondary signals, and subtle alerting
	•	Red is rare and must remain rare
	•	Most of the interface should rely on neutral surfaces and type contrast, not accent saturation

Avoid
	•	neon tones
	•	oversaturated greens
	•	electric cyan
	•	purple sci-fi gradients
	•	dominant red surfaces

⸻

5.2 Typography System

Typography should feel:
	•	technical
	•	elegant
	•	mature
	•	compact
	•	highly readable

Typographic roles

Display / Title
Used for:
	•	recipe title
	•	page headers
	•	archive section titles

Characteristics:
	•	confident
	•	clean
	•	not overly decorative
	•	strong at large and medium sizes

Section Label
Used for:
	•	metadata strip labels
	•	panel headings
	•	archive categories
	•	intake sections

Characteristics:
	•	small uppercase or semi-uppercase
	•	tracking slightly open
	•	low-to-medium emphasis

Body
Used for:
	•	method steps
	•	notes
	•	descriptions
	•	detail copy

Characteristics:
	•	highly legible
	•	moderate line height
	•	optimized for reading on desktop and tablet

Micro / Utility
Used for:
	•	timestamps
	•	revision markers
	•	source tags
	•	small status fields

Characteristics:
	•	compact
	•	lower contrast
	•	still readable

Typography rules
	•	avoid using mono everywhere
	•	mono may be used sparingly for metadata or system tags
	•	recipe instructions should always favor readability over aesthetic posture
	•	kitchen mode should increase size and spacing significantly

⸻

5.3 Shape Language

The system should use:
	•	controlled corner radii
	•	fine divider seams
	•	low-noise framing
	•	panel logic rather than floating cards everywhere

Rules
	•	cards should feel like contained modules, not generic rounded blobs
	•	dividers should be thin and deliberate
	•	shadows should be subtle
	•	edges should feel crisp, not soft and playful

Avoid
	•	overly soft consumer SaaS cards
	•	huge shadows
	•	bubble UI
	•	too many nested outlines

⸻

6. Layout & Hierarchy

6.1 Global layout logic

The product should use a structured application shell.

Recommended layout model:
	•	left filter/navigation rail
	•	central content pane
	•	optional right context pane on desktop
	•	single-column responsive collapse on mobile

Information hierarchy

Every page should answer, in order:
	1.	What is this?
	2.	What matters most here?
	3.	What can I do next?
	4.	What supporting metadata do I need?

⸻

6.2 Screen density

The app should support two density modes in practice:

Standard Mode

Used for:
	•	library browsing
	•	recipe detail
	•	editing
	•	intake

Kitchen Mode

Used for:
	•	cooking from recipe
	•	larger type
	•	simplified controls
	•	reduced visual noise
	•	less metadata, more action

⸻

6.3 Grid behavior

Use a modular grid with:
	•	predictable spacing
	•	consistent alignment
	•	clean content columns
	•	strong rhythm between modules

Desktop

Can support:
	•	two- or three-zone layouts

Tablet

Should prioritize:
	•	stacked but roomy layout

Mobile

Should prioritize:
	•	fast scanning
	•	strong section grouping
	•	thumb-reachable key actions

⸻

7. Core Screen Design Rules

7.1 Library Screen

The Library is the archive control surface.

Purpose
	•	browse recipes
	•	filter recipes
	•	search recipes
	•	enter archive flows

Primary elements
	•	search bar
	•	filter groups
	•	recipe result list/grid
	•	favorites and recent access
	•	archive intake action

Rules
	•	recipe cards must be metadata-rich but not noisy
	•	search must feel immediate
	•	filters must be usable without overwhelming the page
	•	the screen must feel archival, not content-feed-like

⸻

7.2 Recipe Detail Screen

The Recipe Detail view is the dossier page.

Purpose
	•	understand the recipe fully
	•	see metadata quickly
	•	cook from it
	•	refine it
	•	trust it

Primary hierarchy
	1.	Title
	2.	Core metadata strip
	3.	Ingredients
	4.	Method
	5.	Notes / service / pairing
	6.	Source / status / revision

Rules
	•	ingredients and method must dominate the reading hierarchy
	•	metadata should support, not bury, the recipe
	•	service notes should be visible but secondary
	•	images should enrich, not dominate

⸻

7.3 Kitchen Mode

Kitchen Mode is the operational reading surface.

Purpose
	•	make the recipe easy to use while cooking

Rules
	•	larger text
	•	fewer competing elements
	•	strong step separation
	•	clear ingredient visibility
	•	fast access to yield and time
	•	minimal chrome
	•	no unnecessary sidebars or dense metadata panels

Design tone

This should feel:
	•	quiet
	•	focused
	•	robust
	•	legible at a glance

⸻

7.4 Intake / Import Screen

This is where the archive protects itself from chaos.

Purpose
	•	bring messy input into the system cleanly

Input types
	•	raw text
	•	pasted web recipe
	•	URL
	•	image
	•	PDF
	•	manual entry

Rules
	•	clearly separate raw input from cleaned structured output
	•	AI suggestions must never look final until reviewed
	•	show trust/verification state clearly
	•	intake should feel like controlled processing, not magic

⸻

8. Component Language

8.1 Recipe Card

A recipe card should show:
	•	title
	•	key role/cuisine/technique info
	•	timing
	•	yield
	•	favorite/verified state
	•	optional image
	•	brief descriptor or tags

Rules
	•	do not overload with too many badges
	•	keep the title visually dominant
	•	metadata should be organized in a consistent order

⸻

8.2 Metadata Strip

The metadata strip is one of the defining Sevastolink UI elements.

Purpose
	•	compress important facts into a clean readable band

Typical items
	•	role
	•	cuisine
	•	time
	•	yield
	•	complexity
	•	heat window
	•	verified state

Rules
	•	consistent ordering
	•	consistent label treatment
	•	low visual noise
	•	strong readability

⸻

8.3 Status Labels

Status labels should be restrained.

Suggested states:
	•	Verified
	•	Draft
	•	Unverified
	•	Favorite
	•	Revised
	•	Archived

Rules
	•	status should be visible, not loud
	•	green for trusted/verified
	•	amber for advisory/in-review
	•	red only for real faults or destructive actions

⸻

8.4 Inputs and Forms

The intake and edit surfaces should feel precise and structured.

Rules
	•	strong labels
	•	generous vertical spacing
	•	clean focus state
	•	clear field grouping
	•	no ambiguous placeholders replacing labels
	•	support long text comfortably

⸻

8.5 Buttons and Actions

Actions should be grouped by importance:
	•	primary
	•	secondary
	•	utility
	•	destructive

Rules
	•	primary buttons should be calm and deliberate, not flashy
	•	destructive actions must be unmistakable
	•	icon-only controls should be limited and obvious

⸻

9. Motion & Interaction

9.1 Motion philosophy

Motion should be:
	•	subtle
	•	calm
	•	structural
	•	purposeful

Good uses
	•	panel reveals
	•	filter expansion
	•	search/result transitions
	•	mode changes
	•	confirmation states

Avoid
	•	long intros
	•	dramatic sweeping transitions
	•	jitter
	•	fake scanning animations
	•	decorative motion loops

9.2 Hover behavior

Hover should indicate:
	•	readiness
	•	elevation
	•	focus

Not:
	•	glow spectacle
	•	animated noise
	•	aggressive color flashes

9.3 Feedback

System feedback should feel like:
	•	clear acknowledgement
	•	quiet confirmation
	•	calm warnings

Examples:
	•	recipe saved
	•	import normalized
	•	verification changed
	•	image attached
	•	AI unavailable

⸻

10. Content Style & Voice

The UI copy should feel:
	•	clear
	•	restrained
	•	technically literate
	•	calm
	•	not jokey
	•	not theatrical

Good tone
	•	“Recipe normalized”
	•	“Metadata updated”
	•	“Unverified source”
	•	“Kitchen mode enabled”
	•	“LM Studio unavailable”

Avoid
	•	fake ship-computer dialogue
	•	ironic hacker language
	•	overcommitted lore in functional UI

A little Sevastolink flavor is good in names and framing.
The actual interface copy should stay practical.

⸻

11. Accessibility & Usability Rules

The app must prioritize:
	•	strong contrast
	•	readable body text
	•	readable small metadata
	•	clear focus states
	•	touch-friendly controls for tablet/mobile
	•	minimal friction during cooking

Special kitchen considerations
	•	bigger tap targets
	•	stronger spacing
	•	visible timers/time fields
	•	readable under non-ideal lighting
	•	low cognitive load

⸻

12. AI UX Rules

AI should appear as:
	•	assistive
	•	optional
	•	reviewable
	•	structured

AI must never feel like:
	•	the primary interface
	•	a replacement for the archive
	•	a magic black box that silently edits data

Good AI surfaces
	•	“Normalize recipe”
	•	“Suggest metadata”
	•	“Rewrite in archive format”
	•	“Find similar recipes”
	•	“Cook from ingredients”

Required behavior
	•	show source vs AI output clearly
	•	require human review where appropriate
	•	preserve original raw input where useful

⸻

13. Sevastolink Anti-Patterns

Never let the interface become:
	•	terminal cosplay
	•	fake shell prompt UI
	•	neon sci-fi dashboard
	•	gaming HUD
	•	cluttered control wall
	•	overly sparse luxury minimalism with weak usability
	•	visually clever but painful to cook from

⸻

14. Design Direction Summary

The correct Sevastolink direction for this product is:

Galley dossier + operational archive + premium dark utility

That means:
	•	dossier-like recipe pages
	•	controlled metadata rails
	•	structured library surfaces
	•	quiet advisory accents
	•	dark infrastructure styling
	•	high usability under real cooking conditions

⸻

15. Final UI/UX Standard

If a design decision is uncertain, it should be judged by this question:

Does this make the Galley Archive feel more like a trusted domestic command library, or more like a themed interface experiment?

If it feels like an experiment, reject it.
If it improves clarity, trust, and system cohesion, keep it.

⸻

Deliverables this document establishes

This document establishes:
	•	the product’s UI/UX philosophy
	•	the Sevastolink translation rules
	•	the visual direction
	•	layout and hierarchy rules
	•	screen behavior rules
	•	component principles
	•	motion rules
	•	accessibility standards
	•	AI interaction rules
	•	anti-pattern boundaries

⸻

Recommended next documentation page

The next document should be:

Sevastolink Galley Archive — Visual System Spec

That page should define:
	•	exact palette roles
	•	typography tokens
	•	spacing scale
	•	border/radius rules
	•	card variants
	•	metadata strip specs
	•	button/input styles
	•	iconography direction

⸻

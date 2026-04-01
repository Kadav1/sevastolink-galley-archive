# Sevastolink Galley Archive

## Product Brief v1.0

---

## 1. Product Definition

Sevastolink Galley Archive is a local-first, archive-first recipe archive and cooking workspace for home use. It runs as a self-hosted web application on a home server or personal machine, accessible to any device on the home network through a browser. It provides a structured, searchable archive for storing, refining, and retrieving recipes — including personal recipes, transcribed family recipes, imported web recipes, and cookbook references — along with an active cooking workspace for in-kitchen use. Pantry, storage-aware retrieval, and optional AI assistance support the archive rather than replacing it. The product is designed to feel premium, calm, and operational: a serious personal culinary system, not a consumer recipe aggregator or social food app. Optional integration with a local language model (LM Studio) provides AI-assisted normalization, metadata enrichment, and retrieval, but the product is fully functional without it.

This document defines the target product direction and intended product scope. For the current shipped product surface and missing product work, see [implemented-product.md](./implemented-product.md) and [implementation-backlog.md](./implementation-backlog.md).

---

## 2. Core User Scenarios

These are the primary situations the product must serve well.

### 2.1 Finding a recipe when you know roughly what you want

The user opens the archive from the kitchen tablet, searches for chicken dishes that are fast to prepare, and quickly finds a verified recipe they have cooked before. They open it and start cooking.

### 2.2 Capturing a recipe from the web before it disappears

The user finds a recipe on a website. They open the archive, paste the URL or copy the text, and bring it into the system as a draft. The source is preserved. They review it later and decide whether it is worth keeping.

### 2.3 Transcribing a family or handwritten recipe

The user photographs or types out a recipe from a card or notebook. They enter it manually or use AI normalization to structure the text. The result is stored as a personal archive record with source notes.

### 2.4 Cooking from the archive, hands-free

The user opens a recipe on a tablet propped on the counter. The view is clean, large, and readable. Steps are clearly separated. The user does not need to touch the screen frequently.

### 2.5 Building and refining a personal version of a recipe

The user cooks a recipe and makes changes. They open the archive, edit the record, update the notes, and mark it as Verified. The archive reflects how they actually cook the dish now.

### 2.6 Browsing when you want inspiration

The user opens the archive with no specific dish in mind. They browse by cuisine or technique. They find something interesting and explore the record.

### 2.7 Importing a backlog of saved recipes

The user has a large number of bookmarks, notes, and screenshots accumulated over years. They work through them over several sessions, using the intake system to normalize and structure each one. The archive grows gradually and correctly.

### 2.8 Searching by what you have available

The user knows they have specific ingredients and wants to see what archived recipes use them. They search the archive by ingredient. Matching recipes surface.

### 2.9 Deciding what to use soon

The user wants to avoid waste. They look at what is already in the fridge or pantry, see which ingredients or prepared components should be used soon, and use the archive to find suitable recipes or kitchen-use components.

---

## 3. Product Goals

These are ordered by priority. Higher items must be achieved before lower items matter.

### 3.1 Reliable archiving

The product must reliably store recipe records and retrieve them accurately. Data must never be silently lost, corrupted, or overwritten. This is the non-negotiable foundation.

### 3.2 Useful in a kitchen

The product must be readable and functional on a tablet or phone during active cooking. Text must be large enough to read at counter distance. Interaction must not require precision tapping.

### 3.3 Fast, accurate retrieval

The user must be able to find any recipe in the archive quickly. Search by title, ingredient, cuisine, and status must work reliably without requiring AI.

### 3.4 Trustworthy content

The archive must be honest about what is verified and what is not. The user must be able to tell what they have cooked, what they have only saved, and what they have imported but never reviewed.

### 3.5 Clean intake workflow

Bringing recipes into the archive should be fast enough to not feel like work, and structured enough to produce useful records. AI normalization should be available when it helps but never required.

### 3.6 Home-network accessibility

All devices on the home network should be able to reach the archive through a browser without special configuration by the user.

### 3.7 Longevity and resilience

The archive should be something the user can maintain and trust over years. Backup and restore should be straightforward. The data format should not be opaque.

---

## 4. Non-Goals

These are explicitly out of scope. They may seem adjacent but must not be allowed to shape the product.

### 4.1 Not a social platform

No sharing, publishing, following, liking, or commenting. The archive is private and personal.

### 4.2 Not a meal planning application

Meal planning and scheduling are not in scope for v1. The product does not generate weekly menus or shopping lists.

Light planning and scheduling overlays may exist later, but the product does not become a full weekly planning system with complex scheduling logic.

### 4.3 Not a personal nutrition tracking tool

The product does not track daily intake, goals, compliance, or health metrics.

Recipe-level nutrition reference may exist later as advisory metadata on recipe records, but the product is not a diet tracker or health-management application.

### 4.4 Not a grocery or shopping tool

No shopping list generation, no grocery workflow, and no e-commerce integration are in scope unless the product direction is explicitly revised later.

### 4.5 Not a cloud product

No cloud hosting, no cloud sync, no account creation, no cloud backup as a primary path. The product is self-hosted.

### 4.6 Not a general-purpose note-taking app

The product is specific to culinary records. It should not become a general notes tool or knowledge base.

### 4.7 Not an AI chat application

The product does not feature a chat interface, a cooking assistant bot, or a conversational AI layer. AI is used for structured, specific tasks — not conversation.

### 4.8 Not a public recipe aggregator

The product does not scrape, fetch, or sync from recipe services. It does not integrate with third-party recipe databases or APIs.

---

## 5. Functional Scope for v1

v1 is the first complete and usable version. It must be stable, coherent, and genuinely useful as a standalone product.

Current note:

The repository already implements a meaningful subset of this scope, but not every item below is fully surfaced yet in the routed product or API.

### 5.1 Archive

* Store, browse, and search a structured recipe library
* Filter by dish role, cuisine, technique, complexity, time, and trust state
* Full-text search across title, ingredients, and notes
* Support for trusted (Verified), unverified, and draft records

### 5.2 Recipe records

* Title, description, ingredients, steps, timings, serving size
* Source tracking (origin URL, manual entry, file, paste)
* Taxonomy fields: dish role, cuisine, technique family
* Trust state: Draft, Unverified, Verified, Archived
* Personal notes field
* Created and modified timestamps

### 5.3 Intake

* Manual entry
* Paste text with optional AI normalization
* URL capture with raw source preservation
* Review workflow before saving
* Trust state selection at save time

### 5.4 Kitchen Mode

* Focused, clean recipe view optimized for active cooking
* Large text, minimal chrome
* Step-by-step display
* Accessible from tablet and phone

### 5.5 AI normalization (optional)

* LM Studio integration for paste text normalization
* Field-level review of AI suggestions
* AI unavailability handled gracefully
* All AI output requires human approval before saving

### 5.6 Local deployment

* Runs on a home server or personal machine
* Accessible by other devices on the home network through a browser
* No internet required for core operation
* Setup documented and achievable by a non-developer home user

### 5.7 Backup and restore

* Manual export of the full archive
* Import from backup
* Data format documented and human-readable (JSON or SQLite)

---

## 6. Functional Scope for v2

v2 builds on a stable v1. Items here are anticipated but not committed.

### 6.1 Intake improvements

* URL content extraction and AI analysis
* Image and PDF intake with OCR
* Bulk intake workflow for large backlogs

### 6.2 Archive enrichment

* AI-assisted enrichment of existing records
* Re-normalization of poorly structured imports
* Ingredient family tagging at scale

### 6.3 Retrieval improvements

* Natural language search
* Ingredient-based recipe lookup
* Related recipe suggestions
* AI-assisted query interpretation

### 6.4 Storage-aware retrieval

* advisory storage and use-soon guidance tied to archive records
* leftovers and preservation-oriented retrieval
* pantry and fridge input as retrieval context

### 6.5 Collections and organization

* Named collections and folders
* Custom tags beyond taxonomy fields
* Pinned recipes and curated sets

### 6.6 Recipe history and versioning

* Change history on recipe records
* Version comparison
* Revert to earlier version

### 6.7 Expanded media support

* Multiple photos per recipe
* Step-by-step photos
* Source file viewer (PDF, image)

### 6.8 Nutrition reference

* recipe-level nutrition reference metadata
* dietary and allergen cues on recipe records
* retrieval support based on nutrition-related metadata later

### 6.9 Home network improvements

* Configurable hostname and port
* HTTPS on local network
* Optional simple access controls

### 6.10 Meal planning (light)

* Planned date field on recipes
* Simple weekly view of planned dishes
* Not a full planner — just a scheduling overlay

---

## 7. What "Local-First" Means in Practice

Local-first is a functional commitment, not a marketing phrase. For this product it means:

### 7.1 The data lives on the user's hardware

All recipe records, source files, images, and the database reside on the machine running the application. Nothing is stored on a remote server. The user controls the disk. The user owns the data.

### 7.2 The product works without internet

Core archive operations — browsing, searching, reading, editing, saving — must work with no internet connection. The only network requirement is the local home network to reach the server from other devices.

### 7.3 The product works without AI

LM Studio is a local AI runtime. Even so, its availability is not guaranteed. The product must be fully operational when LM Studio is not running, not installed, or not configured.

### 7.4 No external dependencies for core function

No third-party APIs, no cloud services, no remote authentication, and no license servers are required for core operation. The product must not phone home.

### 7.5 Home-network accessibility is built-in

The product binds to an address reachable by other devices on the home network. The user should be able to access their archive from any browser in the house without installing anything on the client device.

### 7.6 Backup is user-controlled and portable

The user must be able to export the archive as a portable file (JSON, SQLite, or equivalent) that they can move, copy, back up to an external drive, and restore on a different machine. No proprietary lock-in.

### 7.7 Longevity is a design constraint

The archive should still be readable and restorable in five years. Formats must not be opaque. Schema changes must be managed with care. The user's data must not be hostage to a running service.

---

## 8. What "AI-Enhanced But Not AI-Dependent" Means in Practice

This phrase defines the relationship between the product and AI precisely.

### 8.1 AI enhances throughput, not capability

Without AI, the user can still manually enter, structure, search, and retrieve every recipe in the archive. AI reduces the effort required — it does not unlock features that would otherwise be unavailable.

### 8.2 Every AI-assisted workflow has a manual alternative

Paste text normalization has a manual editing path. Taxonomy suggestions have manual field selection. Natural language search falls back to field-based search. No user journey dead-ends without AI.

### 8.3 AI availability is surfaced, not hidden

If LM Studio is not running, the interface says so plainly. It does not silently fail, hide AI controls, or pretend nothing is wrong. The user knows their AI is offline and can still work.

### 8.4 AI output is always a proposal

AI never commits data to the archive. Every AI-generated field is a suggestion. The user reviews, edits, and approves before anything is saved. AI cannot change the trust state of a record.

### 8.5 The quality of the archive is the user's responsibility

AI helps the user structure their archive faster. It does not make the archive correct. A Verified recipe is Verified because the user cooked it and trusted it, not because AI processed it.

### 8.6 AI is a local runtime, not a cloud dependency

LM Studio runs on the user's machine. No recipe content is sent to remote AI services by default. The local-first principle extends to AI.

---

## 9. Risks and Failure Modes

### 9.1 Data loss

**Risk:** SQLite corruption, accidental deletion, failed restore.
**Mitigation:** Document clear backup procedure. Provide export as a first-class feature. Write-ahead logging enabled by default. Never perform destructive operations without user confirmation.

### 9.2 Import quality degradation

**Risk:** Users import large numbers of poorly structured recipes and never clean them up. The archive becomes a pile of Unverified drafts.
**Mitigation:** Intake UX makes trust state selection deliberate and visible. Draft and Unverified states are clearly differentiated from Verified in the archive view. Archive health is visible.

### 9.3 AI normalization errors become trusted data

**Risk:** User accepts AI-suggested fields without reviewing them. Incorrect data enters the archive as Verified.
**Mitigation:** Review step is mandatory. Accept-all is possible but requires explicit action. AI badges are visible until the user explicitly approves each field. This is a UX and process constraint, not just a technical one.

### 9.4 Setup complexity blocks use

**Risk:** A non-developer user cannot get the product running on their home server.
**Mitigation:** Deployment must be achievable with a short documented procedure. Docker Compose is the recommended deployment path. A zero-configuration startup with sensible defaults is required.

### 9.5 Kitchen Mode is unusable in the kitchen

**Risk:** The mobile/tablet experience is too small, too dense, or too interactive to use while cooking.
**Mitigation:** Kitchen Mode is treated as a first-class view with its own design and component requirements. It is tested on real tablet-sized screens early.

### 9.6 LM Studio dependency creep

**Risk:** Over time, more and more features are built to require AI, and the non-AI experience degrades.
**Mitigation:** Every new feature must have a non-AI path defined before implementation. The AI Interaction Spec governs this. No core archive operation may be gated behind AI availability.

### 9.7 Schema brittleness

**Risk:** The database schema is changed in a way that breaks existing data or makes migration difficult.
**Mitigation:** Schema changes require migration scripts. No destructive schema changes without a documented migration path. Backup before any schema change.

### 9.8 UI complexity outpaces usefulness

**Risk:** The interface accumulates features and chrome until it is no longer calm and practical.
**Mitigation:** Non-goals are enforced. Every new UI element must serve retrieval, archiving, or kitchen use. The visual system spec constrains decoration.

---

## 10. Final Recommended Product Framing

### What it is

**A personal culinary archive.** Structured, searchable, trustworthy, and private. Built to run on your own hardware, accessible from anywhere in your house, useful in the kitchen.

### What it is not

Not a recipe discovery app. Not a meal planner. Not an AI-first product. Not a social platform. Not a subscription service. Not dependent on any company's infrastructure.

### Who it is for

A home cook who takes their kitchen seriously. Someone who has accumulated recipes across many sources — bookmarks, screenshots, handwritten cards, notes, old emails — and wants a real system to hold them. Someone who values permanence, structure, and their own judgment over algorithmic feeds and recommendation engines.

### The standard it should meet

Open the archive. Find what you need. Cook from it. Come back and update the record when you cook it differently. Trust that it will still be there in five years, exactly as you left it.

Everything in the product design should be measured against that standard.

---

## Decisions Made

1. Product is defined as a local-first personal culinary archive with a self-hosted web UI.
2. Home-network accessibility is a core requirement, not an optional feature.
3. AI is scoped as optional and assistive. No core workflow depends on it.
4. LM Studio is the designated AI runtime. All AI processing is local.
5. v1 scope is bounded: archive, intake (manual + paste + URL), Kitchen Mode, optional AI normalization, local deployment, backup/restore.
6. Meal planning, nutritional tracking, shopping tools, and social features are explicitly out of scope.
7. Verified trust state is user-assigned only. AI cannot set it.
8. Backup is a first-class v1 feature, not deferred.
9. Deployment path is Docker Compose with documented setup procedure.
10. The product is for a single home user or household. Multi-user access control is not a v1 requirement.

---

## Open Questions

1. **Multi-user household access** — Should different household members be able to mark recipes as verified independently, or is there a single trusted user and everyone else reads? This affects trust state design in v2.
2. **Sevastolink overlay fields** — These have been referenced in taxonomy documents but not fully defined here. What specifically distinguishes a Sevastolink-flavored recipe record from a generic one? This needs to be resolved before the schema is written.
3. **Docker Compose vs bare install** — Is Docker Compose the right deployment assumption for the target user? If the user is less technical, a simpler self-contained binary or installer may be needed. This affects v1 architecture choices.
4. **URL import in v1 vs v2** — URL capture (preserve the URL and source, no AI analysis) is listed in v1. Full URL content extraction is listed in v2. The line between these needs to be precise in the Intake spec.
5. **Image storage in v1** — Are recipe photos a v1 feature? The schema and storage model needs to account for this even if the full media management feature is deferred.

---

## Deliverables Created

* `docs/01_product/product-brief.md` — this document

---

## What the Next Prompt Should Cover

**Stage 2 — UI/UX Design Foundations**

Define the visual and interaction language for the product before designing specific screens. This should cover:

* design values and constraints for this product specifically
* how the dark, infrastructural aesthetic is applied without becoming theatrical
* typography principles for archive and kitchen contexts
* layout model for desktop, tablet, and mobile
* how trust state, AI state, and archive status are communicated visually
* what interactions should feel like (speed, weight, feedback)
* component philosophy

Do not design individual screens yet. Define the design system's governing principles.

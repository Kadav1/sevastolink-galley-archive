# Sevastolink Galley Archive

## Intake & Import UX Spec v2.0

---

## 1. Purpose

This document defines the recipe intake system for Sevastolink Galley Archive.

It establishes:

* the intake workflow overview
* the supported intake paths
* how source material becomes structured archive data
* where AI-assisted extraction fits
* validation and review rules
* trust-state logic for imported records
* the recommended v1 and v2 intake flows

This document is the canonical target-state intake and import reference for the product.

Current implementation note:

* the current app only implements `Manual Entry` and `Paste Text`
* URL import, image intake, PDF intake, and broader review queue surfaces are still future-facing
* the CLI importer provides additional bulk-review capability that the web app does not yet expose
* use `docs/10_imports/recipe-import-workflow.md` and `docs/02_ux/implemented-routes-and-flows.md` for current implementation behavior

---

## Current-state gap note

Implemented today:

* intake hub
* manual entry flow
* paste-text intake flow
* optional AI normalization during paste-text intake

Not yet implemented today:

* URL import route and workflow
* image or PDF intake route and workflow
* dedicated intake review route keyed by intake job ID
* broader AI-assisted intake surfaces beyond the current paste-text normalization path

The remainder of this document should therefore be read as target-state intake UX.

---

## 2. Intake philosophy

### Established facts

* The archive must remain structured and trustworthy.
* The system must reduce mess, not create more.
* Raw source, structured candidate, and approved recipe must remain distinct.
* AI is optional and assistive.
* Human review is required before imported material becomes trusted archive data.

### Intake standard

The intake system should feel like a controlled archive gateway, not a magical ingestion box.

The user must always be able to understand:

* what entered the system
* what was extracted
* what was inferred
* what still needs review
* what trust state the result has

### Core rules

* Every intake begins with a source.
* No imported or AI-structured recipe becomes trusted automatically.
* Incomplete records are acceptable when marked clearly.
* Recovery and fallback are required because intake is where messy material enters the archive.

---

## 3. Intake workflow overview

Every intake path should move through the same five-stage model.

### 3.1 Capture

The system receives:

* typed entry
* pasted text
* a URL
* an uploaded image
* an uploaded PDF

The system records:

* intake type
* source snapshot or source reference
* timestamps
* initial workflow state

### 3.2 Extract or structure

The system converts the source into structured candidate data by one of these means:

* direct manual entry
* deterministic parsing
* AI-assisted structuring
* future OCR plus AI-assisted structuring

### 3.3 Validate

The system checks:

* whether enough structure exists
* whether required fields are missing
* whether extraction failed or is partial

### 3.4 Review and edit

The user reviews the candidate against the source, edits it, and resolves uncertainty.

### 3.5 Save with trust state

The user explicitly saves the result as:

* `Draft`
* `Unverified`
* `Verified`

---

## 4. Manual creation workflow

### Role

Manual creation is the most trustworthy intake path.

### Best use cases

* household standards
* already-known recipes
* recipes transcribed from trusted handwritten notes
* refined personal recipes

### Workflow

1. Open `Intake`
2. Choose `Manual Entry`
3. Enter title
4. Enter ingredients
5. Enter steps
6. Add core classification fields
7. Add notes and source context if relevant
8. Save as `Draft`, `Unverified`, or `Verified`

### Required visible fields

* title
* ingredients
* steps
* dish role
* primary cuisine

### Rules

* The form should support incomplete draft saves.
* Manual entry should not force excessive metadata before first save.
* Manual entry may save directly into a recipe record without a separate candidate review screen, because the user is structuring the recipe intentionally.

---

## 5. Text normalization workflow

### Role

Text normalization is the main bridge between messy pasted source and archive structure.

### Best use cases

* copied website text
* note app text
* message threads
* informal recipe writeups

### Workflow

1. Open `Intake`
2. Choose `Paste Text`
3. Paste raw text
4. Preserve raw source immediately
5. Choose:
   * continue manually
   * structure with deterministic help
   * structure with AI
6. Generate structured candidate
7. Review candidate against raw source
8. Edit fields
9. Save with trust state

### Required UX structure

The screen must clearly distinguish:

* raw source text
* structured candidate
* save and trust controls

### Rules

* Original pasted text must remain visible and recoverable.
* Text normalization must never overwrite the source.
* If structuring fails, the user should still be able to store the raw source and continue editing manually.

---

## 6. URL import workflow

### Role

URL import captures recipes that originate on the web while preserving provenance.

### Best use cases

* recipes worth keeping a source URL for
* web references the user may want to revisit
* recipes copied from articles or blogs

### Workflow

1. Open `Intake`
2. Choose `URL Import`
3. Paste URL
4. Fetch page content
5. Preserve URL and fetched source snapshot
6. Attempt extraction
7. Show:
   * source URL
   * source metadata if available
   * extracted text or extracted candidate
8. Review and correct
9. Save with trust state

### Rules

* The URL must be preserved even if extraction fails.
* Extraction failure must fall back to manual cleanup, not a dead end.
* The UI must indicate what was extracted automatically and what remains uncertain.

---

## 7. Image / PDF intake workflow

### Role

Image and PDF intake handles visually sourced recipes and documents.

### Best use cases

* cookbook pages
* screenshots
* scans
* photographed notes
* exported PDFs

### Workflow

1. Open `Intake`
2. Choose `File Intake`
3. Upload image or PDF
4. Store original file locally
5. Show source preview
6. If extraction is available, show extracted text
7. If structuring is available, generate structured candidate
8. Review and edit
9. Save with trust state

### Rules

* Original file must remain linked permanently.
* File-based intake should default toward `Draft` or `Unverified`, never `Verified` automatically.
* Extraction and OCR errors must be easy to correct manually.

---

## 8. AI-assisted structuring workflow

### Role

AI-assisted structuring converts messy source material into a structured candidate.

### Allowed tasks

* title extraction
* ingredient parsing
* step parsing
* timing suggestion
* taxonomy suggestion
* note cleanup
* archive-format rewrite proposal

### Workflow

1. User provides source material
2. User explicitly requests AI assistance
3. System shows processing state
4. Structured candidate is returned
5. AI-generated fields are visibly marked
6. User edits, accepts, or rejects suggestions
7. User saves with trust state

### Rules

* AI is optional at every step.
* AI output must remain reviewable.
* AI suggestions must never look identical to approved archive data.
* AI must never set trust or verification state.

---

## 9. Validation rules

### Validation goals

Validation should protect archive quality without making intake rigid.

### Required checks

* source capture succeeded or a recoverable fallback exists
* title is present before final non-draft approval
* at least one ingredient row exists before final non-draft approval
* at least one step exists before final non-draft approval
* trust state is explicitly chosen at save time
* uploaded files are of supported type
* malformed extracted or AI output is flagged before approval

### Draft tolerance rule

Draft saves may allow missing structure. Unverified and Verified saves require stronger completeness.

### Error handling rules

* preserve user input
* preserve source
* offer manual fallback
* explain next action clearly
* do not discard partial work silently

---

## 10. Human review / edit step

### Role

Review is the trust gate.

### The review screen must show

* title
* source origin
* raw source access
* structured ingredients
* structured steps
* metadata
* notes
* trust-state choice

### Required review actions

* edit field
* accept field
* reject field
* save as draft
* save as unverified
* save as verified
* return to intake source

### Review rules

* Raw source and candidate must remain visibly distinct.
* Uncertainty must remain visible.
* AI suggestions must be marked.
* The user must be able to correct the result without re-running the whole workflow.

---

## 11. Verified vs unverified logic

### Trust states

* `Draft`
* `Unverified`
* `Verified`
* `Archived`

### Meanings

#### Draft

Incomplete or still being shaped.

#### Unverified

Structured enough to store and retrieve, but not yet trusted.

#### Verified

Cooked, checked, or personally trusted.

#### Archived

Preserved but not active in rotation.

### Trust rules

* Imported recipes should usually land as `Draft` or `Unverified`.
* `Verified` must always be an explicit user action.
* AI normalization does not imply trust.
* OCR or extraction success does not imply trust.

---

## 12. Best v1 intake flow

### Recommendation

The best v1 intake flow is:

* `Manual Entry`
* `Paste Text`
* optional AI-assisted normalization from pasted text
* side-by-side review
* save as `Draft`, `Unverified`, or `Verified`

### Why

This gives the product:

* a strong manual path
* a practical messy-text path
* meaningful AI assistance without AI dependency
* manageable implementation scope
* strong trust preservation

### v1 in-scope paths

* Manual creation
* Paste raw text
* AI-assisted text structuring
* Review and approval
* Source retention

### v1 deferred paths

* robust URL extraction
* OCR
* PDF text extraction
* advanced reprocessing
* bulk intake

---

## 13. Best v2 intake flow

### Recommendation

The best v2 intake flow expands the same intake architecture rather than replacing it.

### v2 additions

* stronger URL extraction
* image OCR
* PDF extraction
* AI-assisted structuring from OCR output
* re-run normalization on older candidates
* richer diff and review tooling
* intake deduplication hints

### v2 rule

Even in v2, intake should remain source-first and review-driven. New automation should reduce cleanup work without weakening trust boundaries.

---

## 14. Raw vs structured vs approved model

The intake system must preserve three layers:

### 14.1 Raw source

What originally entered the system.

Examples:

* pasted text
* URL content snapshot
* OCR text
* uploaded image or PDF

### 14.2 Structured candidate

The parsed or AI-assisted interpretation.

Examples:

* extracted ingredients
* extracted steps
* suggested taxonomy
* suggested timings

### 14.3 Approved recipe

The final archive record saved with an explicit trust state.

### Rule

This separation must exist:

* visually
* in workflow logic
* in the data model

---

## 15. Device-specific intake behavior

### Desktop

Best for:

* side-by-side source review
* heavy editing
* taxonomy cleanup
* source comparison

### Tablet

Best for:

* lighter review
* source preview
* photo-assisted intake
* in-kitchen corrections

### Mobile

Best for:

* quick capture
* URL submission
* photo upload
* save as draft
* light review

Deep cleanup should remain comfortable on desktop.

---

## 16. Archive protection rules

The intake system must protect the archive from low-quality drift.

### Required rules

* every import preserves source
* every non-manual import requires review
* AI output is never silently trusted
* incomplete recipes may be stored only with clear status
* trust state must remain visible
* provenance must be retained
* imported recipes must be editable before becoming trusted

---

## 17. Intake anti-patterns

Do not let intake become:

* a black box
* a one-click import-and-trust flow
* an AI-first gimmick
* a hidden transformation pipeline
* a source-destroying simplifier
* an over-formalized admin process

The intake system should feel:

* controlled
* recoverable
* reviewable
* humane

---

## 18. Final intake standard

Every intake decision should be judged by this question:

**Does this make it easier to bring messy culinary material into the archive without damaging trust?**

If not, it does not belong in the intake system.

---

## Decisions made

1. The intake system uses a consistent five-stage workflow: capture, extract/structure, validate, review, save with trust state.
2. Manual entry is the most trustworthy path and may save directly without a separate candidate review screen.
3. Paste Text plus optional AI-assisted structuring is the strongest v1 import flow.
4. URL and file intake preserve source first and tolerate partial extraction.
5. Human review is mandatory for non-manual and AI-assisted intake before trust is raised.
6. `Verified` is always an explicit user action.

## Open questions

1. How much URL extraction should ship in the first implementation versus being deferred?
2. Should v1 support simple deterministic ingredient parsing before AI is configured?
3. How much of raw source should remain expanded by default on mobile review screens?
4. Should image preview stay visible beside extracted text on tablet portrait, or collapse behind a toggle?

## Deliverables created

1. `/docs/02_ux/intake-import-ux.md`

## What document should be created next

`docs/09_ops/local-deployment.md`

This document should define how local intake, file storage, database persistence, backups, and optional LM Studio integration are configured and run in local deployment.

# Sevastolink Galley Archive

## Implemented Routes and Flows v1.0

---

## 1. Purpose

This document defines the currently implemented frontend route structure and user flows.

It establishes:

* which web routes exist in the current app
* what each route does today
* which flows are fully usable
* which routes are placeholders
* how the current UI differs from the broader information architecture and screen specs

This document is implementation-aware and should be read as the current UI baseline.

---

## 2. Route philosophy

### Established facts

* The current frontend is route-based.
* The library is the default landing surface.
* Recipe detail and kitchen mode are distinct route states.
* Intake exists as a routed area with two active paths.
* Settings exists as a route but is not yet a functional configuration surface.

### Current standard

Only the routes listed here should be treated as implemented UI surfaces.

Frontend scaffold directories under `src/features/` and several component subfolders are not evidence of active routed surfaces; the current app is implemented primarily through `pages/`, `hooks/`, `lib/`, and the populated component folders.

---

## 3. Current route map

| Route | Status | Purpose |
|---|---|---|
| `/` | Implemented | Library landing |
| `/library` | Implemented | Library browse surface |
| `/recipe/:slug` | Implemented | Recipe detail |
| `/recipe/:slug/kitchen` | Implemented | Kitchen mode |
| `/intake` | Implemented | Intake hub |
| `/intake/manual` | Implemented | Manual recipe creation |
| `/intake/paste` | Implemented | Paste-text intake and candidate editing |
| `/settings` | Placeholder | Settings page shell only |

---

## 4. Implemented route behavior

### 4.1 Library

Routes:

* `/`
* `/library`

Current role:

* main browse surface for the archive
* entry point into recipe detail

### 4.2 Recipe detail

Route:

* `/recipe/:slug`

Current role:

* display one archive recipe
* support transition into kitchen mode

### 4.3 Kitchen mode

Route:

* `/recipe/:slug/kitchen`

Current role:

* provide a focused cooking surface without the standard app shell navigation

### 4.4 Intake hub

Route:

* `/intake`

Current role:

* present the two active intake paths:
  * manual entry
  * paste text

Current UI note:

* URL import, file intake, and broader AI-assisted intake are shown as later work, not as active routes

### 4.5 Manual entry

Route:

* `/intake/manual`

Current role:

* create a recipe directly in the canonical archive

Current flow:

* user fills in structured recipe fields
* recipe is saved without going through the candidate approval path used by paste-text intake

### 4.6 Paste-text intake

Route:

* `/intake/paste`

Current role:

* create an intake job from raw source text
* optionally run AI normalization
* edit candidate fields
* approve the intake job into a canonical recipe

### 4.7 Settings

Route:

* `/settings`

Current status:

* placeholder only

Current implication:

* configuration remains file-driven, not managed through the UI

---

## 5. Implemented primary flows

### 5.1 Browse to cook

Current flow:

1. Open the library.
2. Select a recipe.
3. Open recipe detail.
4. Enter kitchen mode if needed.

### 5.2 Manual archive entry

Current flow:

1. Open intake hub.
2. Choose manual entry.
3. Enter recipe fields directly.
4. Save into the archive.

### 5.3 Paste-text intake and approval

Current flow:

1. Open intake hub.
2. Choose paste text.
3. Paste raw source text.
4. Create intake job.
5. Optionally run AI normalization.
6. Edit the structured candidate.
7. Approve into the archive.

---

## 6. Current differences from the IA and screen specs

The broader UX docs describe a larger route system than the current app implements.

Not yet implemented in the current frontend:

* `/library/favorites`
* `/library/recent`
* `/library/verified`
* `/library/drafts`
* `/library/search`
* `/recipe/:slug/edit`
* `/intake/url`
* `/intake/file`
* `/intake/review/:id`
* `/ai/*`
* `/settings/*` sub-pages

These remain useful target-state references, but they should not be treated as live UI routes yet.

---

## 7. Contributor note

When adding frontend docs or implementation work:

* describe current routes separately from planned routes
* update this document when a spec-only route becomes real
* avoid documenting placeholder pages as functioning settings or AI workflows

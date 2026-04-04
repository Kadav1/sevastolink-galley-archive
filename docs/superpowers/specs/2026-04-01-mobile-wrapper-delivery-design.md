# Sevastolink Galley Archive

## Mobile Wrapper Delivery Design

Date: 2026-04-01

Status: approved future-state design; implementation deferred

---

## 1. Purpose

This document defines the approved future-state direction for delivering Sevastolink Galley Archive as an installable Android application without turning the current repository into a native-mobile codebase.

It exists to answer a limited set of questions:

* what problem the Android wrapper is meant to solve
* what architectural direction is approved
* where repository ownership should sit
* what must be true before wrapper work should begin
* what this design does and does not commit the project to

This is a target-state design document. It does not change any implementation-aware document, and it does not mean Android work has started.

---

## 2. Documentation Rule

This design must follow the repository's existing documentation policy.

Current-state and implementation-aware documents remain the source of truth for shipped behavior:

* `README.md`
* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/03_visual-system/implemented-visual-system.md`
* `docs/05_ai/implemented-ai.md`
* `docs/06_architecture/implemented-architecture.md`
* `docs/07_api/implemented-api.md`
* `docs/09_ops/implemented-ops.md`

Directional and future-state documents remain the correct place for wrapper planning:

* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/06_architecture/technical-architecture.md`
* `docs/09_ops/local-deployment.md`
* `docs/superpowers/specs/`
* `docs/superpowers/plans/`

Every major idea in this spec is labeled as one of:

* `Implemented now`
* `Already in pipeline`
* `New target-state proposal`
* `Future / not committed`

No implementation-aware document should be updated to describe Android wrapper behavior until wrapper code actually exists.

---

## 3. Decision Summary

The approved future-state direction is:

`a separate Capacitor-based Android wrapper repository that packages the existing Galley web client as an installable app shell while continuing to use the current backend`

This decision means:

* the current repository remains the source of truth for product behavior
* the browser-based product remains the primary implementation
* the Android wrapper is a delivery surface, not a second product client
* the backend remains the system of record
* the project is not committing to React Native, Expo, or a native-first rewrite
* Android delivery is explicitly deferred until the web product is more complete

This decision does not mean:

* that an Android app exists now
* that offline-first mobile support is approved
* that mobile-specific domain behavior should begin diverging from the web product
* that implementation-aware docs should start describing Android behavior

---

## 4. Why The Wrapper Exists

The wrapper is justified only if it improves access to the existing Galley product in situations where a browser tab is a weaker delivery surface.

The strongest reasons for a wrapper are:

* easier launch and re-entry from a phone or tablet home screen
* better kitchen and household access on Android devices
* a more stable installable surface for repeated use than a saved browser tab
* a path to app-level polish around navigation, shell behavior, icons, splash, and permissions

The wrapper is not justified merely because Android packaging is possible.

The product remains:

* archive-first
* local-first in principle
* browser-product-first in implementation
* centered on the same recipe, pantry, intake, and kitchen workflows

The wrapper should only exist if it improves access to that product without creating a second architecture to maintain.

---

## 5. Current-State Classification

### 5.1 Implemented now

These are already true in the repository today:

* a route-based React and Vite frontend exists under `apps/web`
* a separate FastAPI backend exists under `apps/api`
* the current product is delivered as a browser-based experience
* the repository already distinguishes between implementation-aware and target-state documentation

Primary references:

* `docs/00_overview/current-state.md`
* `docs/06_architecture/implemented-architecture.md`
* `docs/07_api/implemented-api.md`

### 5.2 Already in pipeline

These concerns already matter today even though they are not yet Android delivery work:

* phone and tablet usability matters for kitchen use
* deployment posture is still evolving
* environment-specific API behavior already matters in the frontend
* media, upload, and route behavior already need stronger cross-device discipline

Primary references:

* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/09_ops/local-deployment.md`

### 5.3 New target-state proposal

These are new proposals approved by this design:

* create a separate mobile repository rather than converting this repo into a native mobile app
* use Capacitor as the wrapper technology
* package the existing web client rather than reimplementing it
* treat the wrapper as a downstream delivery shell around the existing system
* keep wrapper work deferred until the web product is stable enough to deserve packaging

### 5.4 Future / not committed

These are intentionally not committed by this design:

* React Native or Expo rewrite
* offline-first mobile architecture
* mobile-local database and sync engine
* deep Android-native feature expansion beyond wrapper needs
* a separate mobile product direction with its own domain logic

---

## 6. Product Boundary

The Android wrapper is a delivery vehicle for Galley. It is not a second primary product.

That boundary matters because this project already has a clear product identity:

* the archive is the system core
* the web app is the current implementation
* local hosting and backend ownership matter
* user trust depends on having one coherent archive system, not multiple drifting clients

So the wrapper should be understood as:

* an installable Android surface for the same product
* a packaging and access improvement
* a shell around existing product behavior

It should not become:

* a mobile fork of the UI with separate product behavior
* a place where unfinished web UX is hidden instead of solved
* a back door into building a second frontend architecture before the first one is mature

---

## 7. Repository Boundary And Ownership

The mobile effort should be documented here, but implemented in a separate repository.

This repository remains the source of truth for:

* product direction
* web UI behavior
* backend contracts
* shared types and shared documentation worth reusing
* the rules that govern how a wrapper may relate to Galley

The future mobile repository should own only:

* Capacitor project scaffolding
* Android packaging and signing
* launcher icons, splash assets, manifest configuration, and wrapper metadata
* mobile-specific runtime configuration
* the process that imports a Galley web build into the wrapper

The wrapper must not become a second implementation of Galley.

That means:

* no copied backend code
* no separately maintained mobile fork of the React application
* no product logic divergence unless platform packaging strictly requires it

The intended operating model is:

`this repository defines and builds Galley -> the mobile repository packages Galley for Android`

---

## 8. Quality Bar For The Wrapper

Even as a wrapper, the Android app must meet a real product-quality bar.

The wrapper should feel like:

* a legitimate Android surface for Galley
* readable and touch-safe on phone and tablet
* predictable in navigation and back behavior
* respectful of Android system UI, safe areas, and permission expectations
* suitable for kitchen use, not just casual browsing

That quality bar is especially important because a wrapped web app can easily fail in obvious ways:

* back navigation feels broken or inconsistent
* shell chrome and product chrome fight each other
* controls sit too close to gesture areas or system bars
* layouts technically fit but are poor on tablets or landscape
* uploads, external links, or media flows work in desktop browsers but feel unstable on-device

This design does not require Galley to become visually native in a Material-first sense. It does require the wrapper to feel intentional and competent on Android.

The acceptance test should never be just:

`the website opens inside an APK`

The acceptance test should be:

`the Android wrapper meaningfully improves access to Galley without degrading trust, usability, or coherence`

---

## 9. Readiness Gate

This wrapper should remain deferred until the browser-based product is more complete.

At minimum, wrapper work should not begin until all of the following are true:

* the web product has a stable baseline across library, recipe detail, kitchen mode, pantry, intake, and settings
* the existing phone and tablet experience is already strong enough to justify packaging
* API behavior, media behavior, and runtime configuration are stable enough that the wrapper would not simply absorb avoidable churn
* the product feels coherent enough that installing it on Android would not freeze unfinished UX into a long-lived delivery surface

This gate exists to protect the product from premature packaging work.

If the browser product is still incomplete, the right investment is still:

* finishing missing web routes and workflows
* improving responsiveness and kitchen usability
* stabilizing media and backend behavior
* clarifying deployment and environment handling in the web stack

Until those things are in better shape, this document should be treated as architectural guidance only.

---

## 10. Deferred Technical Planning

Some implementation details are real concerns, but they do not belong at the center of this document yet.

Those later-phase concerns include:

* exact web-artifact handoff workflow between repositories
* backend origin and CORS configuration for Android delivery
* release signing and store packaging details
* shell-level handling of uploads, camera, external links, and Android back behavior
* release traceability between wrapper builds and Galley source commits

Those topics should be handled in a later implementation plan, not treated as reasons to expand this future-state design into a build manual.

---

## 11. Risks And Failure Modes

The wrapper approach is intentionally conservative, but it still has important risks.

### 11.1 Premature packaging

Risk:
The team packages the current web product too early and turns unfinished browser UX into a long-lived Android surface.

Mitigation:
Honor the readiness gate. Do not treat wrapper work as a substitute for improving the web product itself.

### 11.2 Product drift

Risk:
The wrapper starts accumulating mobile-only behavior and becomes a second client architecture.

Mitigation:
Keep ownership boundaries strict. The wrapper packages Galley; it does not redefine Galley.

### 11.3 False offline expectations

Risk:
Users interpret an installable app as meaning offline-first capability exists when it does not.

Mitigation:
Keep scope explicit. This design does not approve offline-first mobile architecture.

### 11.4 Android quality mismatch

Risk:
The wrapper technically works but feels like a browser tab inside a shell, with poor navigation, layout, or touch behavior.

Mitigation:
Use Android quality expectations as a real acceptance bar, especially for kitchen and tablet use.

---

## 12. What This Design Commits To

This design commits to:

* a separate Android wrapper repository
* Capacitor as the approved wrapper technology
* preserving the current repository as the primary implementation
* treating the wrapper as deferred future work
* requiring a meaningful quality bar before wrapper delivery is considered successful

This design does not commit to:

* immediate implementation
* native-mobile rewrite
* offline-first mobile support
* a separate mobile product roadmap

---

## 13. Recommended Next Documentation Step

No immediate implementation plan should be written for the wrapper while the readiness gate is still unmet.

The correct near-term use of this document is:

* keep the wrapper direction recorded and approved
* prevent premature native-mobile drift
* remind contributors that the browser product remains the priority
* preserve a clean boundary between current shipped behavior and future delivery ideas

When wrapper work eventually becomes timely, the next document should be a separate implementation plan that explicitly splits:

* source-repository changes
* mobile-repository work
* Android verification and release concerns

Until then, this design should remain a future-state decision record, not an active build plan.

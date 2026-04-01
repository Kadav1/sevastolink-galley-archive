# Sevastolink Galley Archive

## Mobile Wrapper Delivery Design

Date: 2026-04-01

Status: proposed target-state design

---

## 1. Purpose

This document captures the approved target-state design for delivering Sevastolink Galley Archive as a separate Android wrapper application without converting the current repository into a native mobile codebase.

It defines:

* the approved repository boundary between the current Galley repository and a future mobile wrapper repository
* the recommended wrapper architecture
* how the Android delivery workflow should relate to the existing web and API stack
* key constraints, risks, and verification standards
* which documentation and implementation areas remain current-state versus target-state

This document is a target-state design spec. It does not change the meaning of any implementation-aware document.

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

Target-state and directional documents remain the correct place for broader planning:

* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/06_architecture/technical-architecture.md`
* `docs/09_ops/local-deployment.md`
* `docs/superpowers/plans/`

Every major idea in this spec is labeled as one of:

* `Implemented now`
* `Already in pipeline`
* `New target-state proposal`
* `Future / not committed`

No implementation-aware document should be updated to describe mobile wrapper behavior until that behavior exists in code.

---

## 3. Approved Direction

The approved direction is:

`separate Capacitor-based Android wrapper repository that packages the existing web client as an installable app shell while continuing to use the current FastAPI backend`

This direction is governed by these approved constraints:

* the current repository remains the source of truth for product behavior, web UI, backend contracts, and shared documentation
* the wrapper is a downstream delivery surface, not a second implementation of the product
* the wrapper repository owns Android packaging and runtime concerns only
* the backend remains the system of record
* the wrapper phase does not commit the project to React Native, Expo, or a permanent native-first architecture

This direction does not change current shipped scope by itself.

---

## 4. Current-State Classification

### 4.1 Implemented now

These are already true in the repository today:

* a route-based React and Vite frontend exists under `apps/web`
* a separate FastAPI backend exists under `apps/api`
* the current product is delivered as a browser-based experience
* the repository documentation already distinguishes between current-state and target-state documents

Primary references:

* `docs/00_overview/current-state.md`
* `docs/06_architecture/implemented-architecture.md`
* `docs/07_api/implemented-api.md`

### 4.2 Already in pipeline

These are active concerns already reflected by the current repository structure and documentation, even if they are not yet framed as Android delivery work:

* mobile and tablet usability matters for kitchen use
* packaging and deployment posture is still evolving
* environment-specific API configuration is already partially present in the frontend

Primary references:

* `docs/01_product/product-brief.md`
* `docs/02_ux/ui-ux-foundations.md`
* `docs/09_ops/local-deployment.md`

### 4.3 New target-state proposal

These are new proposals approved by this design:

* create a separate mobile repository rather than converting the current repo into a native mobile app
* use Capacitor as the Android wrapper technology
* package a production build artifact of the current web app into the wrapper
* treat the wrapper as a delivery shell around the existing system rather than a duplicate product implementation

### 4.4 Future / not committed

These are intentionally not committed by this design:

* React Native or Expo rewrite
* true offline-first mobile architecture
* mobile-local database and sync engine
* deep Android-native feature expansion beyond wrapper needs

---

## 5. Repository Boundaries And Ownership

The mobile effort should be documented in this repository, but implemented in a separate repository.

This repository remains the source of truth for:

* product direction
* web UI behavior
* FastAPI backend contracts
* shared type definitions worth reusing
* documentation describing how the mobile wrapper relates to the Galley system

The future mobile repository should own only:

* Capacitor project scaffolding
* Android packaging and signing
* app icons, splash assets, and manifest configuration
* mobile-specific runtime configuration
* the build and import step that brings a Galley web artifact into the wrapper

The wrapper must not become a second product implementation.

That means:

* no copied backend code
* no independently edited fork of the React application as a separate product client
* no duplicated product logic unless Android packaging strictly requires it

The intended operating model is:

`this repository builds and defines Galley -> the mobile repository packages Galley for Android`

---

## 6. Wrapper Architecture

The recommended wrapper architecture is a separate Capacitor-based Android application that packages a production build of the existing web client and connects to the same FastAPI backend.

Core runtime model:

* `apps/web` remains the UI source
* the mobile repository embeds built web assets inside a native Android shell
* the shell loads the application locally on device
* API requests continue to target the existing backend over the network
* the backend remains the system of record

This is not an offline-first mobile architecture. It is an installable Android surface for the current web application.

Required architecture adjustments in the source repository:

* frontend API access must become fully environment-driven rather than split between relative and absolute patterns
* backend CORS and related runtime configuration must allow the wrapper delivery model
* mobile-sensitive flows such as file upload, camera capture, external links, and back navigation must be reviewed against Android runtime expectations

Required architecture in the mobile repository:

* Capacitor project with Android platform support
* scripted import or sync pipeline for Galley web assets
* environment configuration for development, staging, and production backend URLs
* release signing and Play Store packaging setup

Deliberately out of scope for this wrapper phase:

* rewriting the UI in React Native
* mobile-local SQLite persistence
* offline mutation queue and sync engine
* mobile-specific domain logic that diverges from the web app

---

## 7. Build And Delivery Workflow

The wrapper should be built from a production artifact of this repository's web application rather than from a copied working tree.

Recommended flow:

* this repository builds `apps/web`
* the mobile repository imports that build artifact into its Capacitor web assets directory
* the mobile repository runs Capacitor sync and Android build steps
* Android Studio or CI produces APK or AAB outputs

There are two reasonable ways to supply the web artifact:

### 7.1 Archive-based handoff

* this repository produces a versioned archive of the web build
* the mobile repository imports that archive during wrapper release preparation

### 7.2 Git-based handoff

* the mobile repository references this repository at a known commit or tag
* the mobile repository runs a scripted build and import step against that source

Recommendation:

* archive-based handoff should be preferred first because it keeps the wrapper repository simpler and avoids tightly coupling Android packaging to the full Galley source tree

Release ownership must remain explicit:

* web behavior changes are developed here
* Android packaging changes happen in the mobile repository
* each mobile release must record which Galley commit or web artifact it packages

This traceability is required so that a shipped mobile binary can always be mapped back to a specific source state.

---

## 8. Constraints, Risks, And Verification

This wrapper approach has meaningful benefits, but its boundaries should be stated plainly.

### 8.1 Constraints

Primary constraints:

* the app experience is bounded by the current web UI
* true offline use remains limited unless the web app already supports it
* mobile UX quality depends on how well the current routes behave on phone and tablet screens
* Android-native integrations remain shallow unless additional Capacitor plugins are introduced

### 8.2 Repository-specific risks

Known risks in the current codebase:

* recipe API calls currently use relative `/api/v1` paths in `apps/web/src/lib/api.ts`, while media APIs already use `VITE_API_URL` in `apps/web/src/lib/media-api.ts`; this mismatch will create environment and packaging bugs in a wrapper model
* backend CORS is currently tuned for local browser development origins rather than Android delivery
* Android file, camera, and upload flows may behave differently than desktop-browser assumptions
* if the backend is not exposed over stable HTTPS, production Android networking will be fragile and in some cases blocked by platform security defaults

### 8.3 Verification standard

The wrapper phase should not be considered complete until all of the following are true:

* the production web build succeeds
* the wrapper loads the embedded app shell correctly on Android
* core routes work on phone-sized screens
* library, recipe detail, kitchen mode, pantry, intake, and settings connect successfully to the backend
* image and file upload flows are verified on a real Android device
* each release build is traceable to a specific source commit or web artifact version

### 8.4 Product boundary

The wrapper is a delivery vehicle for the existing Galley system. It is not, by itself, a commitment to a permanent mobile architecture.

---

## 9. Recommended Next Documentation Steps

Before implementation planning begins, the repository should keep the documentation split clear:

* this design spec should remain in `docs/superpowers/specs/` as a target-state planning artifact
* implementation-aware documents should not mention mobile wrapper delivery until code exists
* any later implementation plan should explicitly separate source-repo changes from mobile-repo work

When implementation planning starts, the plan should cover:

* frontend API configuration cleanup
* backend CORS and production-origin configuration
* mobile-wrapper repository bootstrap
* artifact handoff workflow
* Android verification and release traceability

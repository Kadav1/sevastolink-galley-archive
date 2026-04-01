# Sevastolink Galley Archive

## Mobile Wrapper Delivery Design

Date: 2026-04-01

Status: approved future-state design; implementation deferred

---

## 1. Purpose

This document captures the approved future-state design for delivering Sevastolink Galley Archive as a separate Android wrapper application without converting the current repository into a native mobile codebase.

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

The approved future-state direction is:

`separate Capacitor-based Android wrapper repository that packages the existing web client as an installable app shell while continuing to use the current FastAPI backend`

This direction is governed by these approved constraints:

* the current repository remains the source of truth for product behavior, web UI, backend contracts, and shared documentation
* the wrapper is a downstream delivery surface, not a second implementation of the product
* the wrapper repository owns Android packaging and runtime concerns only
* the backend remains the system of record
* the wrapper phase does not commit the project to React Native, Expo, or a permanent native-first architecture
* implementation is deferred until the browser-based product is sufficiently complete to justify a wrapper delivery surface

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
* keep the wrapper as a deferred future initiative rather than an active implementation track while the web app remains incomplete

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

### 6.1 Implementation gate

This wrapper should remain a future initiative until the core web product is more complete.

At minimum, wrapper implementation planning should wait until all of the following are true:

* the current browser-based product has a stable and coherent baseline across the major archive, recipe, pantry, intake, and settings surfaces
* the web app is good enough that packaging it would not simply freeze unfinished UX into an Android shell
* responsive and kitchen-mode behavior are already strong enough on phone and tablet screens to justify mobile packaging work
* backend API, media, and environment configuration are stable enough that a wrapper would not be forced to absorb avoidable churn

Until those conditions are met, the correct use of this document is architectural guidance and backlog discipline, not active implementation planning.

---

## 7. Android Design And Quality Guidance

The wrapper is still an Android product surface and should follow Android design and quality guidance rather than behaving like a generic packaged website.

### 7.1 Design philosophy for this wrapper

Google's current Android guidance emphasizes a few principles that are directly relevant here:

* adaptive layouts should be treated as a first-class requirement rather than a later polish pass
* navigation should feel predictable and aligned with Android back behavior
* modern Android apps should support edge-to-edge layouts while respecting system insets and gesture areas
* settings should be limited, well-grouped, and should respect system behavior where possible
* app quality should be judged across user value, user experience, technical quality, and privacy and security rather than only whether the APK launches

For Galley, that means the wrapper should behave like a high-quality Android surface for an archive and kitchen tool, not just a browser tab inside an app shell.

### 7.2 Adaptive layout requirement

Android now treats adaptive design across phones, tablets, foldables, ChromeOS, and multi-window environments as a core quality concern.

For this wrapper, the target should be:

* `Adaptive ready` minimum for the entire wrapper
* selective movement toward `Adaptive optimized` for kitchen-critical routes

Practical implications for Galley:

* the wrapper must be tested in portrait and landscape
* kitchen mode and recipe detail must remain readable on both compact phones and larger tablet surfaces
* tablet and foldable layouts should use available space intentionally rather than merely scaling up phone layouts
* multi-window and split-screen should not break core reading and cooking flows

The wrapper should especially respect the product's existing kitchen-tablet use case rather than optimizing only for narrow phone screens.

### 7.3 Navigation and back behavior

Android guidance treats navigation as a consistency and predictability issue, not just a routing problem.

For this wrapper:

* the Android back action must map cleanly to the web app's route history
* back behavior must not trap the user in modal or shell states unexpectedly
* route transitions should preserve clear mental models of where the user is going next
* any custom handling must avoid fighting Android predictive back expectations

This is particularly important because a wrapped web app can easily feel non-native if back navigation is inconsistent.

### 7.4 Edge-to-edge and inset safety

Current Android guidance expects modern apps to support edge-to-edge layouts while keeping critical content clear of system bars, gesture areas, and display cutouts.

For this wrapper:

* backgrounds and scrolling surfaces may extend edge-to-edge
* tappable controls, step controls, and other critical kitchen actions must remain inset from gesture-conflict areas
* top-level layout review is required for status bar, navigation bar, and cutout overlap
* phone and tablet verification should include gesture navigation and three-button navigation where relevant

This matters for Galley because kitchen use involves fast glances and low-friction interaction; controls placed too close to system gesture zones will degrade usability.

### 7.5 Settings discipline

Android settings guidance is relevant even for a wrapper application.

The wrapper should:

* keep app-specific settings limited to behavior the wrapper truly owns
* avoid duplicating system settings unnecessarily
* use clear language and manageable grouping
* keep frequent actions in context rather than burying them in settings

For example, Android shell concerns such as backend endpoint selection for development may belong in debug-only configuration, while normal product settings should remain owned by the Galley application itself.

### 7.6 Material and Android visual alignment

Google's design guidance points to Material 3 and Android UI conventions as the baseline for a modern Android experience.

This design does not require a visual rewrite of Galley into Material components. It does require:

* respecting Android system bars, safe areas, and navigation conventions
* ensuring launcher assets, splash behavior, and shell-level UI feel coherent with Android norms
* avoiding obvious "desktop web app in a phone frame" failure modes where Android chrome and Galley chrome fight each other

### 7.7 Quality standard for wrapper acceptance

Google's Android quality model should be used as a review lens for the wrapper:

* `Core value`: the wrapper must improve practical access to the archive, especially in kitchen and mobile contexts
* `User experience`: the wrapper must feel predictable, readable, and touch-safe on Android devices
* `Technical quality`: startup, routing, resizing, uploads, and shell integration must be stable across supported devices
* `Privacy and security`: backend access, transport security, and device permissions must be explicit and defensible

This gives the wrapper a stronger acceptance standard than "the site opens inside an app shell".

---

## 8. Build And Delivery Workflow

The wrapper should be built from a production artifact of this repository's web application rather than from a copied working tree.

Recommended flow:

* this repository builds `apps/web`
* the mobile repository imports that build artifact into its Capacitor web assets directory
* the mobile repository runs Capacitor sync and Android build steps
* Android Studio or CI produces APK or AAB outputs

There are two reasonable ways to supply the web artifact:

### 8.1 Archive-based handoff

* this repository produces a versioned archive of the web build
* the mobile repository imports that archive during wrapper release preparation

### 8.2 Git-based handoff

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

## 9. Constraints, Risks, And Verification

This wrapper approach has meaningful benefits, but its boundaries should be stated plainly.

### 9.1 Constraints

Primary constraints:

* the app experience is bounded by the current web UI
* true offline use remains limited unless the web app already supports it
* mobile UX quality depends on how well the current routes behave on phone and tablet screens
* Android-native integrations remain shallow unless additional Capacitor plugins are introduced

### 9.2 Repository-specific risks

Known risks in the current codebase:

* recipe API calls currently use relative `/api/v1` paths in `apps/web/src/lib/api.ts`, while media APIs already use `VITE_API_URL` in `apps/web/src/lib/media-api.ts`; this mismatch will create environment and packaging bugs in a wrapper model
* backend CORS is currently tuned for local browser development origins rather than Android delivery
* Android file, camera, and upload flows may behave differently than desktop-browser assumptions
* if the backend is not exposed over stable HTTPS, production Android networking will be fragile and in some cases blocked by platform security defaults
* if adaptive layouts, insets, and back behavior are not reviewed explicitly, the wrapper will fail Android quality expectations even if the base web app works in a desktop browser

### 9.3 Verification standard

When implementation eventually begins, the wrapper phase should not be considered complete until all of the following are true:

* the production web build succeeds
* the wrapper loads the embedded app shell correctly on Android
* core routes work on phone-sized screens
* tablet and large-screen layouts are reviewed against adaptive-quality expectations for the kitchen and recipe flows
* Android back navigation behaves predictably across route transitions and shell states
* system bars, gesture areas, and display cutouts do not obscure critical controls
* library, recipe detail, kitchen mode, pantry, intake, and settings connect successfully to the backend
* image and file upload flows are verified on a real Android device
* each release build is traceable to a specific source commit or web artifact version

### 9.4 Product boundary

The wrapper is a delivery vehicle for the existing Galley system. It is not, by itself, a commitment to a permanent mobile architecture.

---

## 10. Reference Guidance

The Android-specific guidance in this design is informed by current official Android documentation, especially:

* Android Design & Plan
* Android mobile design guidance
* Android adaptive and large-screen guidance
* Android navigation and predictive back guidance
* Android edge-to-edge design guidance
* Android settings guidance
* Android app quality guidance

These references should be revisited when implementation planning eventually starts so the wrapper plan reflects the then-current Android recommendations.

---

## 11. Recommended Next Documentation Steps

Before implementation planning begins, the repository should keep the documentation split clear:

* this design spec should remain in `docs/superpowers/specs/` as a target-state planning artifact
* implementation-aware documents should not mention mobile wrapper delivery until code exists
* any later implementation plan should explicitly separate source-repo changes from mobile-repo work

Near-term priority should remain on completing the browser-based product.

That means the immediate follow-on work should favor:

* finishing incomplete web routes and workflows
* stabilizing the API and media behavior the web client already depends on
* improving phone and tablet responsiveness inside the existing web application
* deferring wrapper-repository bootstrap until the implementation gate in section `6.1` is met

When implementation planning eventually starts, the plan should cover:

* frontend API configuration cleanup
* backend CORS and production-origin configuration
* mobile-wrapper repository bootstrap
* artifact handoff workflow
* Android verification and release traceability

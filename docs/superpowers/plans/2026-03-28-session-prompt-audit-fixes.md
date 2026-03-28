# Session Prompt Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply all fixes identified in the sessions 13–44 audit: clarify attribution, make dependency chains explicit, document phase-count rationale, add decision frameworks to three open-ended sessions, and create a session dependency map README.

**Architecture:** All changes are editorial edits to Markdown files in `prompts/build/claude/sessions/`. No code, no tests. Verification for each task is reading the file back to confirm the change. Tasks are independent and can be executed in any order.

**Tech Stack:** Markdown only. No build steps required.

---

## File Map

| Task | Files Modified |
|---|---|
| 1 | `session-19-settings-surface.md` |
| 2 | `session-32-settings-domain-and-api.md` |
| 3 | `session-21-shell-navigation-and-context-patterns.md` |
| 4 | `session-24-library-visual-refinement.md` |
| 5 | `session-25-overlay-and-transient-surfaces.md` |
| 6 | `session-26-iconography-and-route-patterns.md` |
| 7 | `session-28-taxonomy-vocabulary-alignment.md` |
| 8 | `session-30-frontend-taxonomy-expansion.md` |
| 9 | `session-31-taxonomy-cleanup-and-drift-repair.md` |
| 10 | `session-37-import-domain-api-and-batch-execution.md` |
| 11 | `session-39-ingredient-first-retrieval-and-inspiration.md` |
| 12 | `session-44-retrieval-assistance-productization.md` |
| 13 | `prompts/build/claude/sessions/README.md` (create) |

All session files live in:
`prompts/build/claude/sessions/`

---

## Task 1: Fix attribution in Session 19

**File:** `prompts/build/claude/sessions/session-19-settings-surface.md`

**Problem:** Line 19 says "Assume previous sessions already established" for the `/settings` route and settings table. These were established in Sessions 1–12, not in the immediately preceding sessions. The vague attribution makes it unclear where these dependencies came from.

- [ ] **Step 1: Apply the edit**

Replace:
```
Assume previous sessions already established:

- routed `/settings` placeholder
- settings table and related schema support in the database
- local file-based `.env` runtime configuration
```

With:
```
Prior work (Sessions 1–12) already established:

- routed `/settings` placeholder
- settings table and related schema support in the database
- local file-based `.env` runtime configuration
```

- [ ] **Step 2: Verify**

Read `session-19-settings-surface.md` lines 18–24. Confirm "Prior work (Sessions 1–12) already established:" appears and "Assume previous sessions" does not.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-19-settings-surface.md
git commit -m "docs(sessions): clarify Session 19 dependency attribution to Sessions 1-12"
```

---

## Task 2: Fix attribution in Session 32

**File:** `prompts/build/claude/sessions/session-32-settings-domain-and-api.md`

**Problem:** Same pattern as Session 19. Line 15 says "Assume previous sessions already established" for the settings UI surface and settings table, which came from prior work not from sessions 23–31.

- [ ] **Step 1: Apply the edit**

Replace:
```
Assume previous sessions already established:

- first real settings UI surface
- current settings table in the database
```

With:
```
Prior work (Sessions 1–19) already established:

- first real settings UI surface
- current settings table in the database
```

- [ ] **Step 2: Verify**

Read `session-32-settings-domain-and-api.md` lines 14–20. Confirm "Prior work (Sessions 1–19) already established:" appears.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-32-settings-domain-and-api.md
git commit -m "docs(sessions): clarify Session 32 dependency attribution to Sessions 1-19"
```

---

## Task 3: Add explicit prerequisites to Session 21

**File:** `prompts/build/claude/sessions/session-21-shell-navigation-and-context-patterns.md`

**Problem:** Session 21 says "at least one additional route group such as edit, settings, or AI tools" but doesn't state which sessions must be complete. A builder running this early would not have the route growth the session expects.

- [ ] **Step 1: Apply the edit**

Replace:
```
Assume previous sessions already established:

- expanded route structure beyond the initial library/intake/detail shell
- at least one additional route group such as edit, settings, or AI tools
```

With:
```
Requires completion of: Sessions 16, 17, 18, 19, and 20 (or at minimum Sessions 17 and 19 for edit and settings routes).

Prior work already established:

- expanded route structure beyond the initial library/intake/detail shell
- at least one additional route group such as edit, settings, or AI tools
```

- [ ] **Step 2: Verify**

Read `session-21-shell-navigation-and-context-patterns.md` lines 14–21. Confirm "Requires completion of:" line appears before the assumption block.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-21-shell-navigation-and-context-patterns.md
git commit -m "docs(sessions): add explicit prerequisites to Session 21"
```

---

## Task 4: Add explicit prerequisites to Session 24

**File:** `prompts/build/claude/sessions/session-24-library-visual-refinement.md`

**Problem:** The assumption block lists "current reusable visual primitives" (Session 23), "current responsive foundation" (Session 22), and "library route expansion" (Session 16) without naming those sessions.

- [ ] **Step 1: Apply the edit**

Replace:
```
Assume previous sessions already established:

- library route expansion
- current responsive foundation
- current reusable visual primitives
```

With:
```
Requires completion of: Session 16 (Library Route Expansion), Session 22 (Responsive Layout Foundation), Session 23 (Reusable Visual Primitives).

Prior work already established:

- library route expansion (Session 16)
- current responsive foundation (Session 22)
- current reusable visual primitives (Session 23)
```

- [ ] **Step 2: Verify**

Read `session-24-library-visual-refinement.md` lines 12–20. Confirm "Requires completion of:" appears with all three sessions named.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-24-library-visual-refinement.md
git commit -m "docs(sessions): add explicit prerequisites to Session 24"
```

---

## Task 5: Add explicit prerequisites to Session 25

**File:** `prompts/build/claude/sessions/session-25-overlay-and-transient-surfaces.md`

**Problem:** Lists "responsive layout foundation" and "reusable visual primitives" as prior work without naming Sessions 22 and 23.

- [ ] **Step 1: Apply the edit**

Replace:
```
Assume previous sessions already established:

- responsive layout foundation
- reusable visual primitives
- at least one workflow that now genuinely needs a transient surface
```

With:
```
Requires completion of: Session 22 (Responsive Layout Foundation), Session 23 (Reusable Visual Primitives).

Prior work already established:

- responsive layout foundation (Session 22)
- reusable visual primitives (Session 23)
- at least one workflow that now genuinely needs a transient surface
```

- [ ] **Step 2: Verify**

Read `session-25-overlay-and-transient-surfaces.md` lines 12–21. Confirm "Requires completion of:" line appears.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-25-overlay-and-transient-surfaces.md
git commit -m "docs(sessions): add explicit prerequisites to Session 25"
```

---

## Task 6: Fix Session 26 prerequisites and conditional language

**File:** `prompts/build/claude/sessions/session-26-iconography-and-route-patterns.md`

**Problem:** (a) Does not name Session 23 as prerequisite. (b) The phrase "settings and/or AI routes if those product areas now exist" is conditional, but both routes are confirmed to exist by this point in the sequence. The hedge creates unnecessary ambiguity.

- [ ] **Step 1: Apply the prerequisite edit**

Replace:
```
Assume previous sessions already established:

- current reusable visual primitives
- settings and/or AI routes if those product areas now exist
```

With:
```
Requires completion of: Session 23 (Reusable Visual Primitives), Session 19 (Settings Surface), Session 20 (AI Tools Area).

Prior work already established:

- current reusable visual primitives (Session 23)
- settings and AI routes (Sessions 19 and 20)
```

- [ ] **Step 2: Apply the session_goal edit — remove the conditional hedge**

Replace:
```
3. tighten visual patterns for settings and AI routes if those routes now exist
```

With:
```
3. tighten visual patterns for settings and AI routes (both are implemented by this point)
```

- [ ] **Step 3: Apply the Phase C inspect edit — remove the conditional**

Replace:
```
   - settings and AI routes if implemented
```

With:
```
   - settings and AI routes (both implemented — Session 19 and Session 20)
```

- [ ] **Step 4: Apply the Phase C implement edit — remove the conditional**

Replace:
```
- stronger settings or AI route visual framing if those routes now exist
```

With:
```
- stronger settings and AI route visual framing (both routes are implemented)
```

- [ ] **Step 5: Verify**

Read `session-26-iconography-and-route-patterns.md`. Confirm "Requires completion of:" line exists, and "if those routes now exist" / "if implemented" / "if those product areas now exist" do not appear anywhere in the file.

```bash
grep -n "if those" prompts/build/claude/sessions/session-26-iconography-and-route-patterns.md
# Expected: no output
```

- [ ] **Step 6: Commit**

```bash
git add prompts/build/claude/sessions/session-26-iconography-and-route-patterns.md
git commit -m "docs(sessions): add prerequisites and remove conditional route hedges from Session 26"
```

---

## Task 7: Add phase-structure note to Session 28

**File:** `prompts/build/claude/sessions/session-28-taxonomy-vocabulary-alignment.md`

**Problem:** This session uses 4 phases (A–D) while most sessions use 5 (A–E). No explanation is given. The documentation-focused work is embedded in Phase C rather than having its own phase, so 4 phases is intentional — but a builder following the template would notice the mismatch without explanation.

- [ ] **Step 1: Apply the edit**

After `</context>` and before `<constraints>`, add a note block. Find this text:
```
</context>

<constraints>
```

Replace with:
```
</context>

<phase_structure_note>
This session uses 4 phases (A–D). Documentation alignment is handled within Phase C rather than in a dedicated phase, so no separate Phase D is needed before the final summary. Phase D here is the final summary.
</phase_structure_note>

<constraints>
```

- [ ] **Step 2: Verify**

Read `session-28-taxonomy-vocabulary-alignment.md`. Confirm `<phase_structure_note>` block appears between `</context>` and `<constraints>`.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-28-taxonomy-vocabulary-alignment.md
git commit -m "docs(sessions): add phase-structure note to Session 28"
```

---

## Task 8: Add phase-structure note to Session 30

**File:** `prompts/build/claude/sessions/session-30-frontend-taxonomy-expansion.md`

**Problem:** Same as Task 7 — uses 4 phases without explanation.

- [ ] **Step 1: Apply the edit**

Find:
```
</context>

<constraints>
```

Replace with:
```
</context>

<phase_structure_note>
This session uses 4 phases (A–D). Documentation alignment is handled within Phase C rather than in a dedicated phase, so no separate Phase D is needed before the final summary. Phase D here is the final summary.
</phase_structure_note>

<constraints>
```

- [ ] **Step 2: Verify**

Read `session-30-frontend-taxonomy-expansion.md`. Confirm `<phase_structure_note>` block appears between `</context>` and `<constraints>`.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-30-frontend-taxonomy-expansion.md
git commit -m "docs(sessions): add phase-structure note to Session 30"
```

---

## Task 9: Add phase-structure note to Session 31

**File:** `prompts/build/claude/sessions/session-31-taxonomy-cleanup-and-drift-repair.md`

**Problem:** Same as Tasks 7–8 — uses 4 phases without explanation.

- [ ] **Step 1: Apply the edit**

Find:
```
</context>

<constraints>
```

Replace with:
```
</context>

<phase_structure_note>
This session uses 4 phases (A–D). Documentation and test coverage are handled within Phase C rather than in a dedicated phase, so no separate Phase D is needed before the final summary. Phase D here is the final summary.
</phase_structure_note>

<constraints>
```

- [ ] **Step 2: Verify**

Read `session-31-taxonomy-cleanup-and-drift-repair.md`. Confirm `<phase_structure_note>` block appears.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-31-taxonomy-cleanup-and-drift-repair.md
git commit -m "docs(sessions): add phase-structure note to Session 31"
```

---

## Task 10: Add decision framework to Session 37

**File:** `prompts/build/claude/sessions/session-37-import-domain-api-and-batch-execution.md`

**Problem:** The session goal says "decide what belongs in an import-domain API versus what should remain script-only" but gives no heuristic for making that decision. A builder has no grounding for the choice, making the outcome underdetermined.

- [ ] **Step 1: Add decision framework to the context block**

Find:
```
Current codebase note:

- bulk imports remain script-driven
- the API exposes intake-job-oriented flows rather than an import-domain API
- background execution for import batches is still absent
- the backlog treats import-domain API and batch execution as later, deliberate decisions
```

Replace with:
```
Current codebase note:

- bulk imports remain script-driven
- the API exposes intake-job-oriented flows rather than an import-domain API
- background execution for import batches is still absent
- the backlog treats import-domain API and batch execution as later, deliberate decisions

Decision framework for Phase A:
When evaluating whether an import operation belongs in the API:
- **API-justified:** operation must be user-initiated from the web UI; needs a real-time response; is already partially modeled by the intake-job flow; would allow the web app to replace a manual CLI step the user currently cannot avoid
- **Script-only (keep as-is):** operation is batch-only; runs offline or in CI; has no interactive web use case today; would require a job queue to be useful (and the queue is not yet warranted)

When evaluating whether batch execution needs background handling:
- **Background-justified:** a real user-facing import workflow already exists that blocks the browser for >5 seconds; the user has no feedback path today
- **Defer:** if no such workflow exists yet, document this as a future decision instead of building speculative infrastructure
```

- [ ] **Step 2: Verify**

Read `session-37-import-domain-api-and-batch-execution.md`. Confirm "Decision framework for Phase A:" appears in the context block.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-37-import-domain-api-and-batch-execution.md
git commit -m "docs(sessions): add decision framework to Session 37 import architecture"
```

---

## Task 11: Fix Session 39 — add pantry endpoint note and decision criteria

**File:** `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`

**Problem:** (a) `POST /pantry/suggest` exists as an implemented backend endpoint but the session doesn't mention it, which could lead a builder to implement it again. (b) "highest-value ingredient-first or inspiration use case" has no evaluation framework.

- [ ] **Step 1: Add pantry endpoint note to the context block**

Find:
```
Current codebase note:

- retrieval already works, but the product brief still calls out ingredient-first search and inspiration browsing as only partially satisfied
- the current app is stronger at "find what you already know" than at "what can I make with this?" or "show me something interesting"
```

Replace with:
```
Current codebase note:

- retrieval already works, but the product brief still calls out ingredient-first search and inspiration browsing as only partially satisfied
- the current app is stronger at "find what you already know" than at "what can I make with this?" or "show me something interesting"
- `POST /pantry/suggest` exists as an implemented backend AI endpoint but has no UI surface yet — this session may surface it or may choose a deterministic alternative; do not rebuild the backend endpoint
- this session owns **deterministic ingredient-first browsing and inspiration discovery** (no AI required); AI-assisted retrieval (pantry suggestion surface, similar-recipe flow) is the domain of Session 44

Decision criteria for "highest-value" in Phase A:
Prioritize a retrieval scenario where:
1. The workflow is impossible or requires 3+ manual steps today, and
2. It does not require AI (deterministic filter/query is sufficient), and
3. It serves a use case the product brief explicitly calls out as underserved ("what can I make with this?" or "show me something interesting")

If all remaining candidates require AI, surface the pantry endpoint (which exists) rather than building new backend logic.
```

- [ ] **Step 2: Verify**

Read `session-39-ingredient-first-retrieval-and-inspiration.md`. Confirm the pantry endpoint note and decision criteria appear in the context block.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md
git commit -m "docs(sessions): add pantry endpoint note and decision criteria to Session 39"
```

---

## Task 12: Fix Session 44 — add boundary statement and decision criteria

**File:** `prompts/build/claude/sessions/session-44-retrieval-assistance-productization.md`

**Problem:** (a) No decision criteria for "highest-value current retrieval-assistance capability." (b) No explicit boundary with Session 39, creating overlap risk on ingredient/pantry territory.

- [ ] **Step 1: Add session boundary note and decision criteria to the context block**

Find:
```
Current codebase note:

- AI retrieval-assistance capabilities exist in the backend
- they are not yet a stronger user-facing product layer
- the backlog leaves this as a later decision after review, enrichment, and diagnostics work
```

Replace with:
```
Current codebase note:

- AI retrieval-assistance capabilities exist in the backend
- they are not yet a stronger user-facing product layer
- the backlog leaves this as a later decision after review, enrichment, and diagnostics work

Session boundary:
- **Session 39** owns ingredient-first browsing and inspiration discovery — deterministic, no AI required
- **This session (Session 44)** owns AI-assisted retrieval surfaces: pantry suggestion (`POST /pantry/suggest`) and similar-recipe finding (`POST /recipes/:id/similar`)
- Do not re-implement or duplicate deterministic ingredient browsing from Session 39 here

Decision criteria for "highest-value" in Phase A:
Choose the AI retrieval capability where:
1. The backend endpoint already exists and is tested (both pantry/suggest and recipes/:id/similar qualify), and
2. There is a clear, narrow UI entry point (e.g., a "What can I cook?" button on the library page, or a "Similar recipes" section on the recipe detail page), and
3. The feature is non-disruptive — it does not replace the default retrieval path, only augments it

Between pantry suggestion and similar-recipe finding: prefer whichever has the clearer user entry point in the current UI. Document the unchosen one as a follow-up.
```

- [ ] **Step 2: Verify**

Read `session-44-retrieval-assistance-productization.md`. Confirm "Session boundary:" block and decision criteria appear in the context block.

- [ ] **Step 3: Commit**

```bash
git add prompts/build/claude/sessions/session-44-retrieval-assistance-productization.md
git commit -m "docs(sessions): add boundary statement and decision criteria to Session 44"
```

---

## Task 13: Create sessions README with dependency map

**File:** `prompts/build/claude/sessions/README.md` (create)

**Problem:** No document maps the execution order or dependency graph. The existing README (if any) may not cover sessions 13–44.

- [ ] **Step 1: Read the existing README to avoid overwriting content**

```bash
cat prompts/build/claude/sessions/README.md
```

- [ ] **Step 2: Write the dependency map section**

Append (or create) the following content. If the file is empty or non-existent, write the full file. If it has existing content, append the Dependency Map section after it.

Content to write or append:

```markdown
## Session Dependency Map (Sessions 13–44)

Sessions must be executed in the order listed. Each session names its prerequisites where they are non-obvious.

### Foundational (no cross-session dependencies)
- **Session 13** — Search Domain and Library Search
- **Session 14** — AI Review and Prompt Family Adoption
- **Session 15** — Dev/Test/Ops Scaffolding

### Library and Edit surfaces
- **Session 16** — Library Route Expansion ← Session 13
- **Session 17** — Recipe Edit Flow (independent)
- **Session 18** — Intake Route Expansion ← Session 14
- **Session 19** — Settings Surface (independent; /settings route established in Sessions 1–12)
- **Session 20** — AI Tools Area ← Session 14

### Shell and Visual System
- **Session 21** — Shell Navigation ← Sessions 16, 17, 18, 19, 20
- **Session 22** — Responsive Layout Foundation (floats on top of current shell)
- **Session 23** — Reusable Visual Primitives ← Session 22
- **Session 24** — Library Visual Refinement ← Sessions 16, 22, 23
- **Session 25** — Overlay and Transient Surfaces ← Sessions 22, 23
- **Session 26** — Iconography and Route Patterns ← Sessions 19, 20, 23

### Taxonomy
- **Session 27** — Shared Taxonomy Foundation (independent)
- **Session 28** — Taxonomy Vocabulary Alignment ← Session 27
- **Session 29** — Taxonomy Validation Expansion ← Sessions 27, 28
- **Session 30** — Frontend Taxonomy Expansion ← Sessions 27, 28, 29
- **Session 31** — Taxonomy Cleanup and Drift Repair ← Sessions 27, 28, 29

### Settings Domain
- **Session 32** — Settings Domain and API ← Sessions 1–19

### Media Domain
- **Session 33** — Media Domain First Slice (independent; media model established in Sessions 1–12)

### API and Database Foundations
- **Session 34** — API Error Envelope Unification (independent)
- **Session 35** — Schema/API Alignment ← Session 34
- **Session 36** — Migration Discipline and Seed Strategy ← Session 35
- **Session 37** — Import Domain API and Batch Execution ← Session 36

### Ops and Observability
- **Session 38** — Ops Scheduling and Observability ← Session 36

### Retrieval and Discovery
- **Session 39** — Ingredient-First Retrieval and Inspiration ← Sessions 13, 16, 30
  - Scope: deterministic ingredient-first browsing; no AI required
  - Note: `POST /pantry/suggest` backend exists — surface it here only if no deterministic alternative is more valuable

### AI Product Workflows
- **Session 40** — Intake Evaluation and Review UX ← Sessions 14, 18
- **Session 41** — Archive Enrichment Workflows ← Sessions 14, 17, 40
- **Session 42** — AI Jobs Visibility Decision ← Sessions 40, 41
- **Session 43** — LM Studio Diagnostics and Health ← Sessions 14, 38

### AI Retrieval Surfaces
- **Session 44** — Retrieval Assistance Productization ← Sessions 39, 40, 43
  - Scope: AI-assisted retrieval only (`POST /pantry/suggest`, `POST /recipes/:id/similar`)
  - Do not duplicate deterministic ingredient browsing from Session 39

---

### Phase Structure Reference

Most sessions use **5 phases** (A–E):
- Phase A: Inspect and plan
- Phase B: Core implementation
- Phase C: Secondary implementation or integration
- Phase D: Docs and alignment
- Phase E: Final summary

Sessions 28, 30, and 31 use **4 phases** (A–D): documentation is embedded in Phase C, so no separate Phase D is needed. Phase D is the final summary.

Sessions 34, 35, 39, 40, 41, 42, 43, and 44 also use **4 phases** for the same reason.
```

- [ ] **Step 3: Verify**

```bash
grep -n "Session 39\|Session 44\|Session boundary\|Phase Structure" prompts/build/claude/sessions/README.md
# Expected: multiple matches covering the boundary and phase notes
```

- [ ] **Step 4: Commit**

```bash
git add prompts/build/claude/sessions/README.md
git commit -m "docs(sessions): add dependency map and phase structure reference to README"
```

---

## Self-Review

**Spec coverage check:**

| Audit finding | Task |
|---|---|
| Session 19: vague "previous sessions" attribution | Task 1 |
| Session 32: vague "previous sessions" attribution | Task 2 |
| Session 21: implicit dependency chain | Task 3 |
| Session 24: implicit dependency chain | Task 4 |
| Session 25: implicit dependency chain | Task 5 |
| Session 26: implicit dependencies + conditional hedge | Task 6 |
| Sessions 28, 30, 31: phase count inconsistency | Tasks 7, 8, 9 |
| Session 37: no decision framework | Task 10 |
| Session 39: no decision criteria + pantry endpoint unacknowledged | Task 11 |
| Session 44: no decision criteria + overlap risk with Session 39 | Task 12 |
| All sessions: no session dependency map | Task 13 |

All audit findings have a corresponding task. No gaps.

**Placeholder scan:** No "TBD", "TODO", or vague instructions. Every step shows exact before/after text.

**Consistency check:** Session numbers referenced in Task 13's README match the numbers used in Tasks 1–12. Session 39's boundary note (Task 11) and Session 44's boundary note (Task 12) are mirror-consistent — one says "this session owns deterministic browsing," the other says "this session owns AI surfaces."

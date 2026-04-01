# Operational Cooking Hub Doc Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align target-state product and UX docs with the approved Operational Cooking Hub design without violating the repository's implementation-aware documentation policy.

**Architecture:** This slice is documentation-first and deliberately narrow. It updates only target-state planning documents so the approved direction becomes official product guidance, while leaving implementation-aware docs untouched until code lands. The plan also reconciles the approved design with the existing session pipeline so already-implemented and already-planned work are not accidentally reintroduced as new scope.

**Tech Stack:** Markdown docs, `rg`, `sed`, `git`

---

## Scope Split

The approved spec covers multiple independent subsystems. This plan intentionally covers only the prerequisite alignment slice:

* adopt the approved direction in target-state product docs
* reconcile backlog docs with the existing session pipeline
* record storage guidance as a genuine new proposal
* record recipe-level nutrition reference as a proposal gated on brief revision

Follow-on plans are still required for:

* Session `39` execution and deterministic ingredient-first retrieval
* first-class storage-guidance product surfaces
* recipe-level nutrition metadata schema and UI work

---

## File Map

### Target-state docs to modify

* `docs/01_product/product-brief.md`
  * canonical target-state product scope; update product framing, non-goals, and v2 boundaries
* `docs/01_product/implementation-backlog.md`
  * product backlog; distinguish existing pipeline work from genuinely new proposals
* `docs/02_ux/information-architecture.md`
  * target-state IA; clarify where stronger pantry/storage guidance belongs
* `docs/02_ux/implementation-backlog.md`
  * UX backlog; note that deterministic ingredient-first retrieval is already owned by Session `39` and add storage-guidance work as new proposal

### Reference docs to inspect but not modify in this slice

* `docs/superpowers/specs/2026-03-30-operational-cooking-hub-design.md`
* `docs/superpowers/sessions.md`
* `prompts/build/claude/sessions/README.md`
* `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`
* `docs/00_overview/current-state.md`
* `docs/05_ai/implemented-ai.md`

### Docs explicitly out of scope for edits

* `docs/00_overview/current-state.md`
* `docs/01_product/implemented-product.md`
* `docs/02_ux/implemented-routes-and-flows.md`
* `docs/05_ai/implemented-ai.md`
* `docs/07_api/implemented-api.md`

---

### Task 1: Align the Product Brief with the Approved Direction

**Files:**
- Modify: `docs/01_product/product-brief.md`
- Inspect: `docs/superpowers/specs/2026-03-30-operational-cooking-hub-design.md`
- Inspect: `docs/00_overview/current-state.md`

- [ ] **Step 1: Verify the current brief still blocks recipe-level nutrition reference and understates storage-aware retrieval**

Run:

```bash
rg -n "Not a nutritional tracking tool|Not a grocery or shopping tool|meal planning|ingredient-based recipe lookup" docs/01_product/product-brief.md
```

Expected:

* matches for the current nutrition non-goal and planning/grocery boundaries
* no explicit support for recipe-level nutrition reference
* no strong storage-aware retrieval framing beyond current archive scenarios

- [ ] **Step 2: Update the product definition and scenarios with the approved framing**

Add or revise wording in `docs/01_product/product-brief.md` so it includes text equivalent to:

```md
Sevastolink Galley Archive is a local-first recipe archive and cooking workspace for home use. It is archive-first: recipes, sources, trust state, and refinement history remain the system core. Pantry, storage-awareness, and optional AI retrieval assist the archive rather than replacing it.

### 2.x Deciding what to use soon

The user wants to avoid waste. They look at what is already in the fridge or pantry, see which ingredients or prepared components should be used soon, and use the archive to find suitable recipes or kitchen-use components.
```

Requirements:

* preserve the archive-first and local-first identity
* keep pantry/storage guidance subordinate to the archive
* do not imply new shipped behavior

- [ ] **Step 3: Rewrite the nutrition and planning boundaries to match the approved direction**

Replace the nutrition non-goal language with wording equivalent to:

```md
### 4.3 Not a personal nutrition tracking tool

The product does not track daily intake, goals, compliance, or health metrics.

Recipe-level nutrition reference may exist later as advisory metadata on recipe records, but the product is not a diet tracker or health-management application.
```

Keep planning and shopping bounded with wording equivalent to:

```md
### 4.2 Not a full meal planning application

Light planning and scheduling overlays may exist later, but the product does not become a full weekly planning system with complex scheduling logic.

### 4.4 Not a grocery or shopping tool

No shopping list generation, no grocery workflow, and no e-commerce integration are in scope unless the product direction is explicitly revised later.
```

- [ ] **Step 4: Add narrow v2 language for storage guidance and nutrition reference**

Add or revise v2-scope wording so it includes concrete items such as:

```md
### 6.x Storage-aware retrieval

* advisory storage and use-soon guidance tied to archive records
* leftovers and preservation-oriented retrieval
* pantry and fridge input as retrieval context

### 6.x Nutrition reference

* recipe-level nutrition reference metadata
* dietary and allergen cues on recipe records
* retrieval support based on nutrition-related metadata later
```

Constraints:

* phrase these as target-state directions, not shipped commitments
* do not add personal tracking or grocery logic

- [ ] **Step 5: Run a targeted sanity check on the revised brief**

Run:

```bash
rg -n "recipe-level nutrition reference|storage-aware|use-soon|personal nutrition tracking|shopping list" docs/01_product/product-brief.md
```

Expected:

* matches for `recipe-level nutrition reference`, `storage-aware`, and `use-soon`
* no language that turns the product into a shopping tool

- [ ] **Step 6: Commit the product-brief update**

Run:

```bash
git add docs/01_product/product-brief.md
git commit -m "docs: align product brief with operational cooking hub direction"
```

Expected:

* one commit touching only the target-state brief for this task

---

### Task 2: Reconcile the Product Backlog with Existing Sessions and New Proposals

**Files:**
- Modify: `docs/01_product/implementation-backlog.md`
- Inspect: `docs/superpowers/sessions.md`
- Inspect: `prompts/build/claude/sessions/README.md`
- Inspect: `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`

- [ ] **Step 1: Verify the current product backlog does not distinguish pipeline work from new proposals**

Run:

```bash
sed -n '1,220p' docs/01_product/implementation-backlog.md
```

Expected:

* generic backlog buckets
* no explicit separation between implemented work, session-owned work, and genuinely new proposals

- [ ] **Step 2: Add a classification note tied to the approved design**

Insert a short note near the top of `docs/01_product/implementation-backlog.md` with wording equivalent to:

```md
Backlog items in this document should be read through four lenses:

* implemented now
* already in pipeline
* new target-state proposal
* future / not committed

Use the implementation-aware docs and `docs/superpowers/sessions.md` before treating a product idea as missing work.
```

- [ ] **Step 3: Rewrite retrieval and browsing expansion to recognize Session 39 ownership**

Revise the retrieval section so it includes text equivalent to:

```md
Missing work:

* recent, verified, and draft-oriented views
* stronger inspiration browsing by cuisine or technique
* clearer ingredient-first retrieval

Planning note:

* deterministic ingredient-first retrieval is already owned by Session 39 and should not be reintroduced as a separate greenfield proposal
```

- [ ] **Step 4: Add storage guidance and nutrition reference as deliberate later product layers**

Revise the later product layers section to include text equivalent to:

```md
Missing work:

* storage guidance as a first-class advisory product layer
* stronger use-soon and leftovers-aware retrieval
* recipe-level nutrition reference metadata, only after the product brief revision is accepted

These should remain secondary until the core archive, intake, and retrieval pipeline work is complete.
```

- [ ] **Step 5: Verify the backlog now reflects session and proposal boundaries**

Run:

```bash
rg -n "Session 39|storage guidance|nutrition reference|future / not committed|already in pipeline" docs/01_product/implementation-backlog.md
```

Expected:

* a match for `Session 39`
* a match for `storage guidance`
* a match for `nutrition reference`

- [ ] **Step 6: Commit the product backlog update**

Run:

```bash
git add docs/01_product/implementation-backlog.md
git commit -m "docs: reconcile product backlog with cooking hub roadmap"
```

Expected:

* one commit for the backlog alignment only

---

### Task 3: Update the Information Architecture for Archive-Connected Storage Guidance

**Files:**
- Modify: `docs/02_ux/information-architecture.md`
- Inspect: `docs/02_ux/ui-ux-foundations.md`
- Inspect: `docs/superpowers/specs/2026-03-30-operational-cooking-hub-design.md`

- [ ] **Step 1: Confirm the current IA mentions pantry and AI tools but does not clearly place storage guidance**

Run:

```bash
rg -n "AI Tools|pantry|storage|planning|shopping list" docs/02_ux/information-architecture.md
```

Expected:

* pantry- and storage-related mentions exist
* no clear archive-connected storage-guidance module or use-soon framing

- [ ] **Step 2: Add archive-connected storage-awareness language to the IA philosophy and product structure**

Revise `docs/02_ux/information-architecture.md` with wording equivalent to:

```md
The architecture should optimize for:

* retrieval
* use
* intake
* preservation
* storage-aware decision support

Storage-aware decision support helps the user answer what should be used soon, how a recipe or component fits pantry conditions, and which archive records are best suited to current household ingredients.
```

Also clarify in the product-structure model that storage guidance is a supporting layer within archive and pantry flows, not a new top-level app separate from the archive.

- [ ] **Step 3: Update the app map and route notes without inventing shipped routes**

Add target-state wording such as:

```md
Library and pantry flows may later surface:

* use-soon contexts
* leftovers and preservation-oriented retrieval
* storage-reference support linked from recipe and pantry views
```

Constraints:

* do not document these as currently implemented routes
* keep them clearly target-state

- [ ] **Step 4: Verify the IA still avoids grocery/planner drift**

Run:

```bash
rg -n "shopping list|grocery|inventory platform|use-soon|storage-reference" docs/02_ux/information-architecture.md
```

Expected:

* matches for `use-soon` or `storage-reference`
* no new wording that turns the IA into a grocery/inventory system

- [ ] **Step 5: Commit the IA update**

Run:

```bash
git add docs/02_ux/information-architecture.md
git commit -m "docs: add storage-aware guidance to target-state IA"
```

Expected:

* one commit touching only the IA doc for this task

---

### Task 4: Reconcile the UX Backlog with Session 39 and Add Storage Guidance as New Work

**Files:**
- Modify: `docs/02_ux/implementation-backlog.md`
- Inspect: `docs/superpowers/sessions.md`
- Inspect: `prompts/build/claude/sessions/session-39-ingredient-first-retrieval-and-inspiration.md`
- Inspect: `prompts/build/claude/sessions/session-44-retrieval-assistance-productization.md`

- [ ] **Step 1: Inspect the current UX backlog entries for AI tools and retrieval**

Run:

```bash
sed -n '1,260p' docs/02_ux/implementation-backlog.md
```

Expected:

* AI tools and retrieval expansion are described broadly
* no explicit note that deterministic ingredient-first retrieval is already session-owned

- [ ] **Step 2: Add a backlog note distinguishing deterministic and AI retrieval work**

Insert wording equivalent to:

```md
Retrieval note:

* deterministic ingredient-first retrieval and inspiration are already owned by Session 39
* AI-assisted pantry and similar-recipe surfacing are already implemented in a first slice and should now be treated as refinement work rather than greenfield capability
```

- [ ] **Step 3: Add storage-guidance surfaces as a new proposal rather than pretending they are already planned**

Extend the backlog detail with text equivalent to:

```md
New target-state proposal:

* storage-guidance surfaces tied to recipe detail and pantry workflows
* advisory use-soon / caution modules
* leftovers and preservation-oriented retrieval framing

These are not yet owned by an existing implementation session and should remain proposal-level until a dedicated plan or session is created.
```

- [ ] **Step 4: Verify the UX backlog now cleanly separates session-owned work from new work**

Run:

```bash
rg -n "Session 39|already implemented|new target-state proposal|storage-guidance|use-soon" docs/02_ux/implementation-backlog.md
```

Expected:

* a match for `Session 39`
* a match for `storage-guidance` or `use-soon`
* wording that does not reclassify implemented AI retrieval as missing greenfield work

- [ ] **Step 5: Commit the UX backlog update**

Run:

```bash
git add docs/02_ux/implementation-backlog.md
git commit -m "docs: reconcile UX backlog with retrieval pipeline"
```

Expected:

* one commit for the UX backlog alignment

---

### Task 5: Run a Cross-Doc Consistency Pass and Protect the Current-State Boundary

**Files:**
- Inspect: `docs/01_product/product-brief.md`
- Inspect: `docs/01_product/implementation-backlog.md`
- Inspect: `docs/02_ux/information-architecture.md`
- Inspect: `docs/02_ux/implementation-backlog.md`
- Inspect only: `docs/00_overview/current-state.md`
- Inspect only: `docs/05_ai/implemented-ai.md`

- [ ] **Step 1: Search the revised docs for contradiction-prone language**

Run:

```bash
rg -n "implemented now|already in pipeline|new target-state proposal|future / not committed|shopping list|personal nutrition tracking|use-soon|Session 39" docs/01_product/product-brief.md docs/01_product/implementation-backlog.md docs/02_ux/information-architecture.md docs/02_ux/implementation-backlog.md
```

Expected:

* target-state docs contain the new framing
* there is no text authorizing shopping lists or personal tracking

- [ ] **Step 2: Verify implementation-aware docs were not touched**

Run:

```bash
git diff --name-only -- docs/00_overview/current-state.md docs/01_product/implemented-product.md docs/02_ux/implemented-routes-and-flows.md docs/05_ai/implemented-ai.md docs/07_api/implemented-api.md
```

Expected:

* no output

- [ ] **Step 3: Read the final affected sections to confirm the language is target-state, not shipped behavior**

Run:

```bash
sed -n '1,260p' docs/01_product/product-brief.md
sed -n '1,220p' docs/01_product/implementation-backlog.md
sed -n '1,260p' docs/02_ux/information-architecture.md
sed -n '1,260p' docs/02_ux/implementation-backlog.md
```

Expected:

* pantry/storage guidance is framed as target-state
* nutrition is bounded to recipe-level reference only
* implementation-aware docs remain untouched

- [ ] **Step 4: Run a final git status check**

Run:

```bash
git status --short
```

Expected:

* only the four target-state docs from this plan are newly modified in this slice
* pre-existing unrelated workspace changes may still be present and must be left alone

- [ ] **Step 5: Commit the final consistency pass if any small wording fixes were needed**

Run:

```bash
git add docs/01_product/product-brief.md docs/01_product/implementation-backlog.md docs/02_ux/information-architecture.md docs/02_ux/implementation-backlog.md
git commit -m "docs: finalize operational cooking hub target-state alignment"
```

Expected:

* final docs-only commit for any last cross-doc wording fixes

---

## Post-Plan Follow-On Work

After this plan is complete, the next plans should be:

1. `2026-04-01-session-39-ingredient-first-retrieval-plan.md`
2. `2026-04-01-storage-guidance-module-plan.md`
3. `2026-04-01-recipe-nutrition-reference-plan.md`

The first should execute already-approved session-owned work. The latter two should remain blocked until the doc-alignment slice lands cleanly.

---

## Self-Review Notes

### Spec coverage

This plan covers the parts of the approved spec that explicitly required documentation changes:

* product-brief revision for recipe-level nutrition reference
* IA clarification for storage-aware guidance
* backlog reconciliation against implemented and session-owned work
* preservation of the current-state documentation boundary

It does not implement Session `39`, storage guidance UI, or nutrition metadata in code. Those require follow-on plans by design.

### Placeholder scan

No placeholder markers or vague deferred steps are left in task steps. Each step contains exact files, commands, and the concrete wording or direction to add.

### Type consistency

The plan uses the same classification language throughout:

* `Implemented now`
* `Already in pipeline`
* `New target-state proposal`
* `Future / not committed`

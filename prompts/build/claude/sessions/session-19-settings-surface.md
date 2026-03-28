<role>
You are the implementation lead for Sevastolink Galley Archive working inside a real repository.
</role>

<context>
This repository already has canonical foundation documents and implementation-aware docs. Treat them as source of truth unless explicitly revised:

- docs/00_overview/current-state.md
- docs/01_product/product-brief.md
- docs/02_ux/information-architecture.md
- docs/02_ux/screen-blueprint-pack.md
- docs/02_ux/component-inventory.md
- docs/02_ux/implemented-routes-and-flows.md
- docs/02_ux/implementation-backlog.md
- docs/07_api/implemented-api.md
- docs/08_database/implemented-database.md
- docs/09_ops/configuration-reference.md

Prior work (Sessions 1–12) already established:

- routed `/settings` placeholder
- settings table and related schema support in the database
- local file-based `.env` runtime configuration

Current codebase note:

- the current settings page is a placeholder only
- the UX docs describe broader settings groupings than the app currently exposes
- some configuration is runtime/file-driven and should not be casually editable in-browser
- the repo needs a practical first settings slice, not a fake full control plane
</context>

<constraints>
Do not imply that every `.env` variable should become a browser-editable setting.
Keep file-based runtime configuration and product preferences conceptually separate.
Prefer settings that already have real runtime or UX effect.
Do not broaden into operator/admin APIs beyond what this slice truly needs.
</constraints>

<session_goal>
Implement the first real settings product slice by building these layers in order:

1. settings information architecture for what belongs in-product now
2. functional settings landing page
3. one or two serious settings groups with persistence where appropriate
4. explicit distinction between browser/product preferences and file-driven ops config
5. implementation-aware docs updates

The result should replace the placeholder page with a real but honest settings surface.
</session_goal>

<required_process>
You must follow this exact process.

PHASE A — Inspect
Before making changes:
1. Read the relevant docs again
2. Inspect:
   - `apps/web/src/pages/SettingsPage.tsx`
   - any settings-related backend models/routes/services
   - settings schema/storage usage
   - current ops/config docs
3. Identify:
   - which settings already have meaningful runtime effect
   - which settings should remain file-driven only
   - the smallest safe in-product settings slice

Then output:
- a concise current-state assessment
- a short implementation plan
- the exact files you expect to create or modify
- the commands you expect to run for verification

Do not edit files before this assessment is complete.

PHASE B — Implement settings foundation
Read again as needed:
- docs/02_ux/information-architecture.md
- docs/09_ops/configuration-reference.md
- docs/08_database/implemented-database.md

Implement:
- practical settings grouping for current product needs
- backend/settings handling only if required for real persistence
- clear boundary between persisted product preferences and non-UI runtime config

Requirements:
- keep the scope narrow and honest
- avoid pretending `.env` editing is now part of the product
- align storage with what the repo already supports

After this phase:
- run focused verification
- summarize only this phase before moving on

PHASE C — Implement settings UI
Read again as needed:
- docs/02_ux/screen-blueprint-pack.md
- docs/02_ux/component-inventory.md
- docs/03_visual-system/visual-system-spec.md

Implement:
- real `/settings` landing surface
- one or two serious settings groups
- loading, save, and error states

Requirements:
- keep the page structured and operational
- do not create empty sub-pages just to match the target-state IA
- expose only settings that are actually implemented

After this phase:
- run focused verification
- summarize only this phase before moving on

PHASE D — Docs and route alignment
Implement/update:
- `docs/02_ux/implemented-routes-and-flows.md`
- implementation-aware settings/ops docs touched by this work

Requirements:
- document the real settings surface and its limits
- avoid overstating runtime configurability

After this phase:
- run focused verification
- summarize only this phase before final summary

PHASE E — Final summary
At the end, provide exactly these sections:

1. Files changed
2. What works now
3. What remains next
4. Commands to run locally
5. Assumptions or doc conflicts
</required_process>

<editing_rules>
- Only create or modify files needed for this slice
- Do not broaden into AI tools or backup/system admin surfaces
- Do not add empty settings subsections
</editing_rules>

<verification_rules>
Use the narrowest useful checks after each phase.
Examples:
- frontend build
- focused settings API tests if created
- settings persistence smoke checks

If you cannot verify something locally, state exactly what could not be verified and why.
</verification_rules>

<output_style>
Be concise, structured, and implementation-focused.
Do not write long essays.
Do not skip the planning step.
Do not skip the per-phase summaries.
</output_style>

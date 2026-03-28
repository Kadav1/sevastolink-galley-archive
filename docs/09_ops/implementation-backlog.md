# Sevastolink Galley Archive

## Operations Implementation Backlog v1.0

---

## 1. Purpose

This document lists the main operations work still missing between the current repo and the broader target-state ops model.

It complements:

* [implemented-ops.md](./implemented-ops.md)
* [local-deployment.md](./local-deployment.md)
* [backup-restore.md](./backup-restore.md)
* [configuration-reference.md](./configuration-reference.md)

---

## 2. Priority summary

### P1

* add real `scripts/dev` helpers
* add real `scripts/migrate` helpers
* add real `scripts/seed` helpers
* resolve whether embeddings configuration should stay future-facing or become live

### P2

* formalize scheduled backup guidance or add a helper wrapper
* improve operator observability and routine troubleshooting workflows
* tighten the documented single-machine deployment path around compose, nginx, and systemd

### P3

* decide whether backup, system, or settings operations should be surfaced via HTTP APIs
* add richer admin/operator tooling only if the product still needs it

---

## 3. Backlog details

### 3.1 Dev command layer

Current state:

* the repo relies on the root `Makefile`
* `scripts/dev/` exists as reserved structure but has no implemented helpers

Missing work:

* optional wrapper scripts for common local workflows
* repeatable operator shortcuts beyond raw `make` targets
* clearer split between developer and operator commands if the repo keeps growing

### 3.2 Migration workflow

Current state:

* database initialization and migration behavior are implemented in the application
* there is no dedicated operator-facing migration command layer in `scripts/migrate/`

Missing work:

* explicit migration entrypoints
* clearer operator procedure for applying schema changes outside normal startup
* migration verification guidance for future schema revisions

### 3.3 Seed workflow

Current state:

* the repo includes a reserved `scripts/seed/` directory
* there is no implemented seed-data workflow

Missing work:

* decide whether seed data is actually needed
* add seed/reset helpers if local demos or onboarding need them

### 3.4 Scheduled backups

Current state:

* backup and restore are implemented
* retention pruning is implemented
* automated scheduling is only documented as an example cron entry

Missing work:

* optional helper for host cron or systemd timer installation
* stronger retention recommendations
* clearer backup verification workflow if the archive grows

### 3.5 Observability and troubleshooting

Current state:

* operators have compose logs, nginx logs, journalctl, and health endpoints
* there is no broader status dashboard or richer diagnostics surface

Missing work:

* clearer runtime troubleshooting checklist
* optional helper targets for common diagnostics
* stronger visibility into LM Studio connectivity if AI remains an important local dependency

### 3.6 Future operator APIs

Current state:

* operations remain shell- and compose-driven
* there are no implemented HTTP resources for backup, system state, or runtime settings administration

Missing work:

* decide whether these capabilities should remain local-only workflows
* only implement admin APIs if they materially improve the product

---

## 4. Recommended implementation order

1. `scripts/migrate` and `scripts/dev`
2. `scripts/seed` decision and implementation if still justified
3. scheduled backup helper or timer guidance
4. observability improvements
5. only then consider admin/operator APIs

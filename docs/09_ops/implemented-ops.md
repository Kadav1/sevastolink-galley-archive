# Sevastolink Galley Archive

## Implemented Operations v1.0

---

## 1. Purpose

This document defines the current implemented operations model for Sevastolink Galley Archive.

It is the implementation-aware companion to:

* [local-deployment.md](./local-deployment.md)
* [backup-restore.md](./backup-restore.md)
* [configuration-reference.md](./configuration-reference.md)

Use this document when the question is:

* what operator workflows exist today
* which runtime surfaces are actually implemented
* which ops areas remain shell-driven or placeholder-only

---

## 2. Current operational baseline

### Established facts

* The repository supports local operation through Docker Compose.
* The repository also supports direct local API and web runs without Docker.
* nginx is implemented as an optional reverse-proxy layer under the compose `proxy` profile.
* Linux user-level systemd units are implemented for boot/login-managed startup.
* Backup and restore are implemented as local shell scripts.
* Runtime configuration is file-based through a root `.env` file.
* LM Studio is optional and runs outside the compose stack.

### Current ops standard

The implemented operator surface is:

* compose and `make` for lifecycle management
* shell scripts for backup and restore
* `.env` for configuration
* optional nginx and systemd helpers for single-machine deployment

There is no broader operator UI or dedicated admin API surface today.

---

## 3. Implemented operator surfaces

### 3.1 Compose and Makefile workflow

Current operator entrypoints are implemented in the root `Makefile`.

Established commands include:

* `make up`
* `make up-detach`
* `make up-proxy`
* `make up-proxy-detach`
* `make down`
* `make restart`
* `make logs`
* `make logs-api`
* `make logs-web`
* `make logs-nginx`
* `make ps`
* `make build`
* `make rebuild`
* `make shell-api`
* `make shell-web`
* `make init-data`
* `make backup`
* `make backup-db`
* `make backup-list`
* `make backup-prune`
* `make restore BACKUP=...`
* `make test-api`

Interpretation:

* the Makefile is the current primary operator interface
* these commands are real and implementation-backed
* there is no parallel higher-level `scripts/dev` command layer yet

### 3.2 Local deployment model

Current local deployment supports:

* `galley-api` in Docker Compose
* `galley-web` in Docker Compose
* optional `galley-nginx` in Docker Compose
* direct local backend run with `uvicorn`
* direct local frontend run with `npm run dev`

Interpretation:

* the project is currently optimized for local single-machine deployment
* there is no Kubernetes, cloud deployment, or hosted ops layer in the repo

### 3.3 Reverse proxy

nginx is implemented as an optional runtime layer.

Current behavior:

* enabled only with the compose `proxy` profile
* routes `/api/*` and FastAPI docs paths to the backend
* routes all other paths to the web frontend
* keeps direct `:3000` and `:8000` access available

Interpretation:

* nginx is real and operational
* it is optional convenience infrastructure, not the only supported runtime path

### 3.4 systemd integration

Linux user-level systemd integration is implemented.

Current behavior:

* unit files exist for standard and proxy variants
* an install script copies them into `~/.config/systemd/user/`
* units wrap `docker compose` rather than replacing the compose stack

Interpretation:

* systemd support is real and usable
* it is still a single-host convenience layer around Docker Compose

### 3.5 Backup and restore

Backup and restore are implemented and operational.

Current behavior:

* backups are directory-based and local
* database backup uses `sqlite3 .backup` when available
* restore is interactive by default
* restore never auto-applies `.env`
* backup pruning is manual

Interpretation:

* backup and restore are first-class local workflows
* there is no automated scheduler or remote backup target in the repo

### 3.6 Configuration

Runtime configuration is implemented through `.env` plus Docker Compose and backend settings.

Current behavior:

* backend settings are read via Pydantic settings
* Docker Compose consumes the root `.env`
* the web container is configured through compose environment and Vite defaults
* LM Studio remains an external dependency configured by URL and model id

Interpretation:

* configuration is implementation-backed and documented
* not every variable in `.env.example` is currently live in backend settings

---

## 4. Current missing or incomplete operations areas

### Established facts

The repository still has several reserved or partially realized operations areas.

Current gaps include:

* no implemented `scripts/dev` helper layer
* no implemented `scripts/migrate` helper layer
* no implemented `scripts/seed` helper layer
* no built-in scheduled backup tooling
* no richer admin or operator API for backups, system state, or settings
* no active embeddings runtime despite `EMBEDDINGS_DIR` in `.env.example`

### Current interpretation

Operations are functional today, but they remain intentionally simple:

* lifecycle is compose-driven
* data protection is shell-script-driven
* migrations happen through application startup/init behavior rather than explicit operator commands
* operational visibility is mostly logs and container status, not dedicated dashboards or endpoints

---

## 5. Config consumption notes

### Established facts

The backend settings model currently consumes:

* `NODE_ENV`
* `API_PORT`
* `DATABASE_URL`
* `MEDIA_DIR`
* `IMPORTS_DIR`
* `EXPORTS_DIR`
* `BACKUPS_DIR`
* `LM_STUDIO_ENABLED`
* `LM_STUDIO_BASE_URL`
* `LM_STUDIO_MODEL`

Variables present in `.env.example` but not currently consumed by backend settings include:

* `PORT`
* `NGINX_PORT`
* `EMBEDDINGS_DIR`

Interpretation:

* `PORT` and `NGINX_PORT` are still meaningful at the compose/runtime layer
* `EMBEDDINGS_DIR` is currently future-facing

---

## 6. Recommended reading order

Use the ops docs in this order:

1. this document for current implemented ops scope
2. [configuration-reference.md](./configuration-reference.md) for env behavior
3. [local-deployment.md](./local-deployment.md) for runtime setup
4. [backup-restore.md](./backup-restore.md) for data protection workflows
5. [implementation-backlog.md](./implementation-backlog.md) for missing ops work

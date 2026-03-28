# Sevastolink Galley Archive

## Configuration Reference v1.0

---

## 1. Purpose

This document defines the current runtime configuration model for Sevastolink Galley Archive.

It establishes:

* the environment variables used by the local stack
* which service consumes each variable
* the current defaults
* which values are optional
* where Docker and non-Docker behavior differs
* which variables are present but not yet meaningfully consumed

This is an implementation-aware companion to `.env.example`, local deployment guidance, and the application settings code.

For the wider implemented ops surface and remaining operations gaps, see [implemented-ops.md](./implemented-ops.md) and [implementation-backlog.md](./implementation-backlog.md).

---

## 2. Configuration philosophy

### Established facts

* Configuration is local and file-based.
* The repository expects a root `.env` file derived from `.env.example`.
* The backend reads configuration through Pydantic settings.
* Docker Compose also consumes root-level environment values.
* Not every variable present in `.env.example` currently has equivalent live behavior in application code.

### Configuration standard

Configuration documentation should distinguish clearly between:

* values consumed by Docker Compose
* values consumed by the FastAPI backend
* values consumed by the frontend toolchain
* values reserved for future use

---

## 3. Root configuration file

Create the local environment file once:

```bash
cp .env.example .env
```

The project expects `.env` at the repository root.

---

## 4. Variable reference

| Variable | Default | Consumed by | Required | Notes |
|---|---|---|---|---|
| `NODE_ENV` | `development` | Backend settings, general local conventions | No | Currently low-impact |
| `PORT` | `3000` | Docker/web runtime | No | Web UI port |
| `API_PORT` | `8000` | Backend settings, Docker | No | FastAPI port |
| `NGINX_PORT` | `8080` | Docker proxy profile | No | Used by `make up-proxy` |
| `DATABASE_URL` | `sqlite:./data/db/galley.sqlite` | Backend | No | Normalized internally to SQLAlchemy SQLite form |
| `MEDIA_DIR` | `./data/media` | Backend | No | Local media path |
| `IMPORTS_DIR` | `./data/imports` | Backend | No | Raw and parsed import tree |
| `EXPORTS_DIR` | `./data/exports` | Backend | No | Reserved export path |
| `BACKUPS_DIR` | `./data/backups` | Backend | No | Backup destination path |
| `LM_STUDIO_ENABLED` | `false` | Backend | No | Gates AI normalization |
| `LM_STUDIO_BASE_URL` | `http://localhost:1234/v1` | Backend | No | Adjust for Docker or LAN use |
| `LM_STUDIO_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | Backend | No | Recommended tested default |
| `EMBEDDINGS_DIR` | `./data/embeddings` | Not currently consumed in app settings | No | Future-facing at present |

---

## 5. Variable details

### 5.1 App and routing variables

#### `NODE_ENV`

Current role:

* available to the backend settings model
* used as a conventional environment marker only

#### `PORT`

Current role:

* used for the web service runtime
* determines the main frontend access port in local Docker use

#### `API_PORT`

Current role:

* used by the backend service
* determines the FastAPI port in local Docker and local development

#### `NGINX_PORT`

Current role:

* used only when the nginx proxy profile is enabled

Use this when:

* running `make up-proxy`
* exposing both frontend and backend through a single port

### 5.2 Data path variables

#### `DATABASE_URL`

Current role:

* sets the SQLite database location

Current behavior:

* the backend normalizes bare `sqlite:./...` values into SQLAlchemy-compatible SQLite URLs

#### `MEDIA_DIR`

Current role:

* defines the filesystem path for media assets

#### `IMPORTS_DIR`

Current role:

* defines the root imports path used by the backend

#### `EXPORTS_DIR`

Current role:

* defines the local exports path

Current note:

* export workflows are not yet a major surfaced feature, but the path is part of the current settings model

#### `BACKUPS_DIR`

Current role:

* defines the backup path used by the application environment

Current note:

* backup and restore are currently run through shell scripts rather than an HTTP API

### 5.3 LM Studio variables

#### `LM_STUDIO_ENABLED`

Current role:

* enables or disables AI normalization in the backend

When `false`:

* paste-text intake remains usable
* normalization calls return an AI-disabled error
* manual completion remains available

#### `LM_STUDIO_BASE_URL`

Current role:

* sets the LM Studio HTTP base URL used by the backend client

Common values:

* local host process outside Docker: `http://localhost:1234/v1`
* host machine from Docker container: `http://host.docker.internal:1234/v1`
* LAN-hosted LM Studio: `http://192.168.1.x:1234/v1`

#### `LM_STUDIO_MODEL`

Current role:

* selects the model identifier sent to LM Studio for normalization

Current note:

* `Qwen/Qwen2.5-7B-Instruct` is the repository's current recommended default

### 5.4 Future-facing variable

#### `EMBEDDINGS_DIR`

Current status:

* present in `.env.example`
* not currently part of the backend settings model
* not currently used by the implemented web or API flows

Interpretation:

* this is reserved configuration for future retrieval or embeddings work
* it should not be treated as an active current dependency

---

## 6. Docker and non-Docker differences

### Docker use

Under Docker:

* the frontend and backend run in containers
* LM Studio is still expected to run outside the stack
* `LM_STUDIO_BASE_URL` usually needs `host.docker.internal` rather than `localhost`

### Non-Docker use

Without Docker:

* the backend and frontend run directly from the local repo
* `http://localhost:1234/v1` is usually the correct LM Studio base URL

---

## 7. Required minimum configurations

### Basic non-AI local run

Minimum useful configuration:

* `PORT`
* `API_PORT`
* `DATABASE_URL`

In practice, copying `.env.example` as-is is enough for a local non-AI run.

### AI-enabled local run

Minimum additional AI settings:

* `LM_STUDIO_ENABLED=true`
* `LM_STUDIO_BASE_URL=<reachable-v1-base-url>`
* `LM_STUDIO_MODEL=<installed-model-name>`

---

## 8. Current implementation caveats

### Established facts

The root environment file contains a mix of:

* active variables
* operational convenience values
* future-facing placeholders

### Current caveats

* `EMBEDDINGS_DIR` is not yet wired into the backend settings object
* the current settings page in the web UI is only a placeholder and does not edit these values
* configuration remains file-driven, not UI-driven

---

## 9. Recommended practice

For current local use:

* start from `.env.example`
* change LM Studio settings only when enabling AI
* avoid moving data directories casually
* treat `.env` as machine-local operational state

For documentation and contributor work:

* do not assume a variable is live merely because it appears in `.env.example`
* verify whether it is consumed by Compose, the backend settings model, or neither

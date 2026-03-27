# Sevastolink Galley Archive

Local-first recipe archive and cooking workspace with Sevastolink UI language and optional LM Studio integration.

---

## Running

### With Docker (recommended)

```bash
cp .env.example .env        # configure once
make up                     # builds images, creates data dirs, starts services
```

- Web UI: http://localhost:3000
- API: http://localhost:8000/api/health

`make up` calls `init-data` first, which creates `data/db`, `data/media`, `data/imports`, `data/exports`, and `data/backups` on the host. These directories are bind-mounted into the API container and persist across rebuilds.

### Without Docker (local dev)

```bash
# API
cd apps/api
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# Web (separate terminal)
cd apps/web
npm install
npm run dev
```

---

## Current status

This repository contains both:

* implemented product behavior
* broader target-state specification documents

For implementation-aware documentation, start with:

* `docs/00_overview/current-state.md`
* `docs/07_api/implemented-api.md`
* `docs/10_imports/recipe-import-workflow.md`
* `docs/09_ops/configuration-reference.md`
* `docs/02_ux/implemented-routes-and-flows.md`

The larger spec documents under `docs/` remain canonical design references, but they describe more surface area than is currently implemented in code.

The repository also contains scaffold directories kept with `.gitkeep` for planned areas such as search, media, feature modules, and higher-level test layers. Those directories are reserved structure, not proof that code is missing from the checkout. See `docs/00_overview/current-state.md`.

---

## Make targets

| Target | Description |
|---|---|
| `make up` | Build images and start all services (foreground) |
| `make up-detach` | Start in background |
| `make up-proxy` | Start with nginx reverse proxy on port 8080 |
| `make down` | Stop all services |
| `make restart` | Restart all services |
| `make logs` | Tail all service logs |
| `make logs-api` | Tail API logs only |
| `make logs-web` | Tail web logs only |
| `make logs-nginx` | Tail nginx logs (requires `up-proxy`) |
| `make ps` | Show running containers |
| `make build` | Build images without starting |
| `make rebuild` | Build images with no cache |
| `make shell-api` | Open a shell in the API container |
| `make shell-web` | Open a shell in the web container |
| `make init-data` | Create host-side data directories |
| `make backup` | Create timestamped backup in `data/backups/` |
| `make backup-db` | Database-only backup |
| `make backup-list` | List available backups |
| `make backup-prune` | Remove backups older than 30 days (`KEEP_DAYS=N`) |
| `make restore BACKUP=<path>` | Restore from a backup directory |
| `make test-api` | Run API test suite |
| `make clean` | Remove containers and images (does not touch `data/`) |

---

## Data persistence

All recipe data lives under `data/` at the repo root:

```
data/db/          SQLite database (galley.sqlite)
data/media/       Recipe photos and media assets
data/imports/     Raw source files (preserved, never modified)
data/exports/     Backup/restore archives
data/backups/     Database snapshots
```

These directories are bind-mounted into the API container. Removing containers or images does not affect them. `make clean` removes containers and images but does **not** delete the `data/` bind mounts.

### Backup

```bash
make backup          # full backup: db + media + imports
make backup-db       # database only
make backup-list     # see what's available
make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
```

See `docs/09_ops/backup-restore.md` for full backup, restore, and retention guidance.

---

## LM Studio (optional)

LM Studio runs on your host machine — not inside Docker. AI features are disabled by default.

To enable:

1. Start LM Studio and load a model
2. In `.env`, set:
   ```
   LM_STUDIO_ENABLED=true
   LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
   LM_STUDIO_MODEL=<your-model-name>
   ```
3. Restart the API: `make restart`

`host.docker.internal` resolves to your host machine from inside Docker containers on Linux (via the `extra_hosts` mapping in `docker-compose.yml`). For LAN-hosted LM Studio, use the machine's IP address directly.

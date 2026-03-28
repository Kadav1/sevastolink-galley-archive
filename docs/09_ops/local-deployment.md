# Local Deployment

## Overview

Sevastolink Galley Archive runs as two local services:

| Service | Role | Default address |
|---|---|---|
| `galley-api` | FastAPI backend, SQLite, media | http://localhost:8000 |
| `galley-web` | React frontend (Vite dev server) | http://localhost:3000 |

Both services are defined in `docker-compose.yml`. You run them together with `make up`.

LM Studio is a separate optional process you run on your own machine. It is not part of the compose stack.

This document describes the current implemented local deployment path. For the current ops baseline and missing areas, see [implemented-ops.md](./implemented-ops.md) and [implementation-backlog.md](./implementation-backlog.md).

---

## Prerequisites

- Docker and Docker Compose (Docker Desktop or Docker Engine + Compose plugin)
- A `.env` file at the repo root (copy from `.env.example` once)

```bash
cp .env.example .env
```

You do not need Python or Node installed locally — Docker handles them inside containers.

---

## First run

```bash
cp .env.example .env      # one-time config setup
make up                   # creates data dirs, builds images, starts services
```

`make up` calls `init-data` first, which creates the required directories under `data/` if they don't exist.

Open the app at http://localhost:3000.

---

## Normal daily workflow

| Goal | Command |
|---|---|
| Start the app | `make up` (foreground) or `make up-detach` (background) |
| Stop the app | `make down` (or Ctrl-C if running foreground) |
| Restart | `make restart` |
| Watch logs | `make logs` |
| Watch API logs only | `make logs-api` |
| See what's running | `make ps` |

---

## Rebuilding after code changes

The source is volume-mounted and both services run in auto-reload mode, so ordinary code edits take effect without rebuilding.

Rebuild the Docker images only when dependencies change (new pip packages, npm packages):

```bash
make rebuild    # builds with no cache
make up         # restart with rebuilt images
```

---

## Persistent data

All data lives under `data/` at the repo root. This directory is bind-mounted into the API container — it is **not** stored inside Docker's internal storage and is **not** removed by `make clean` or `docker compose down`.

```
data/
  db/           galley.sqlite — the recipe database
  media/        uploaded photos and media assets
  imports/      raw source files (preserved as imported, never modified)
  exports/      user-generated archive exports
  backups/      timestamped backup snapshots (created by make backup)
  logs/         application logs
```

Do not move or rename these directories without also updating `.env` and the compose volume mounts.

---

## LM Studio (optional AI)

LM Studio runs on your host machine as a separate process. It is not started by `make up`.

To enable AI features:

1. Start LM Studio and load a model (recommended: `Qwen/Qwen2.5-7B-Instruct`).
2. In `.env`:
   ```
   LM_STUDIO_ENABLED=true
   LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
   LM_STUDIO_MODEL=<your-model-name>
   ```
3. `make restart` to reload config.

`host.docker.internal` resolves to the host machine from inside Docker containers on Linux. If LM Studio is on another machine on your LAN, use that machine's IP directly:
```
LM_STUDIO_BASE_URL=http://192.168.1.91:1234/v1
```

If LM Studio is unavailable, the app continues to work. AI-dependent features (normalize, suggest) return an unavailable error. All archive functions work without it.

---

## Running without Docker

```bash
# API — from apps/api/
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# Web — from apps/web/ (separate terminal)
npm install
npm run dev
```

In this mode the Vite proxy targets `http://localhost:8000` by default (no `API_HOST` env needed), and data paths resolve relative to the repo root.

---

## nginx reverse proxy (optional)

By default, the app runs on two ports: the web UI on `:3000` and the API on `:8000`. This is fine for normal localhost use.

nginx is available as an opt-in layer that routes both through a single port (default: `8080`). It is useful when:
- you want a single URL with no port number (e.g. on a home network, `http://galley.local`)
- you want to access the archive from another device without remembering two ports

It is **not** needed for normal localhost development.

### Starting with nginx

```bash
make up-proxy          # foreground
make up-proxy-detach   # background
```

When running, both access paths work simultaneously:

| URL | What serves it |
|---|---|
| http://localhost:8080 | nginx → frontend |
| http://localhost:8080/api/ | nginx → backend |
| http://localhost:3000 | Vite directly (still active) |
| http://localhost:8000 | FastAPI directly (still active) |

### Routing

nginx routes requests as follows:
- `/api/*` → `galley-api:8000`
- `/docs`, `/redoc`, `/openapi.json` → `galley-api:8000` (FastAPI auto-docs)
- everything else → `galley-web:3000`

Vite's built-in `/api` proxy is bypassed when the browser accesses the app through nginx — the browser talks to nginx at port 8080, and nginx handles the routing to the backend directly.

### Port configuration

The nginx port defaults to `8080`. To change it, set `NGINX_PORT` in `.env`:

```
NGINX_PORT=80    # standard HTTP — may require root on some systems
NGINX_PORT=9090  # any available port
```

### Home-network access

Because nginx listens on all interfaces (`server_name _;`), it is reachable by the host's LAN IP without config changes:

```
http://192.168.1.x:8080     # from another device on your home network
```

To use a hostname instead of an IP, add the hostname to `/etc/hosts` on each device, or configure your router's local DNS.

### Logs

```bash
make logs-nginx
```

---

## systemd service (optional, Linux only)

systemd unit files are provided so the archive can start automatically on boot on Linux hosts. This is optional — `make up` and `make up-detach` continue to work independently.

The unit files wrap `docker compose` directly. systemd manages the docker compose process; Docker manages the containers. No additional Python or Node setup is needed on the host.

### Prerequisites

- Linux host with systemd
- Docker installed and the user in the `docker` group (`sudo usermod -aG docker $USER`)
- Repo cloned and `.env` configured (`cp .env.example .env`)
- Images built at least once (`make build` from the repo root)
- Data directories created (`make init-data` from the repo root)

### Install

```bash
# From the repo root:
bash infra/systemd/install.sh           # basic stack (no nginx)
bash infra/systemd/install.sh proxy     # with nginx reverse proxy
```

The script copies the unit file to `~/.config/systemd/user/` and reloads the daemon. It prints a warning if the repo path does not match the default assumption (`~/sevastolink-galley-archive`).

**If the repo is not at `~/sevastolink-galley-archive`**, edit the installed unit file after installation:

```bash
# Open the unit file in your editor:
systemctl --user edit --full galley
# Change the two lines:
#   WorkingDirectory=  →  absolute path to the repo
#   EnvironmentFile=   →  absolute path to .env
```

### Enable and start

```bash
systemctl --user enable galley    # start on login
systemctl --user start galley     # start now
```

For the proxy variant:

```bash
systemctl --user enable galley-proxy
systemctl --user start galley-proxy
```

Do not enable both `galley` and `galley-proxy` at the same time — they would conflict on ports.

### Start on boot without logging in

By default, user services only start when the user logs in. To start on boot:

```bash
loginctl enable-linger $USER
```

This is the recommended setting for a home-server use case where the machine reboots and the archive should be available without a login session.

### Stop and restart

```bash
systemctl --user stop galley
systemctl --user restart galley
systemctl --user status galley
```

### View logs

```bash
journalctl --user -u galley -f          # tail live
journalctl --user -u galley -n 100      # last 100 lines
journalctl --user -u galley --since today
```

Container output from all services is captured in the journal.

### Update procedure

After pulling new code or changing dependencies:

```bash
systemctl --user stop galley
cd /path/to/repo
make rebuild        # rebuild images
systemctl --user start galley
```

If only `.env` changed:

```bash
systemctl --user restart galley   # reloads EnvironmentFile on start
```

### Backup and restore interaction

The service accesses the same `data/` directories as `make up`. Backups and restores work the same way regardless of how the service was started.

Before restoring:

```bash
systemctl --user stop galley
make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
systemctl --user start galley
```

### Disable and remove

```bash
systemctl --user stop galley
systemctl --user disable galley
rm ~/.config/systemd/user/galley.service
systemctl --user daemon-reload
```

---

## Health check

```
GET http://localhost:8000/api/health
```

Returns `{"status": "ok"}` when the API is running and the database is reachable.

Via nginx: `GET http://localhost:8080/api/health`

---

## Command reference

Run `make help` for the full list of available targets.

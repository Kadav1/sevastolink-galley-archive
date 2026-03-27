# Backup and Restore

## Overview

Backup and restore are first-class operations for Sevastolink Galley Archive. The archive is a personal record — its data is irreplaceable.

All backup and restore operations are file-based, local, and human-inspectable. There is no cloud backup dependency.

---

## What needs to be backed up

| Path | Contents | Included in backup |
|---|---|---|
| `data/db/galley.sqlite` | All recipes, intake jobs, candidates, settings | Yes — always |
| `data/media/` | Uploaded photos and media assets | Yes |
| `data/imports/` | Raw source files preserved from intake | Yes |
| `data/exports/` | User-generated exports | Not included — back up manually if needed |
| `.env` | Configuration snapshot | Copied as `env.bak` reference; not used by restore |

---

## Backup

### Full backup

```bash
make backup
```

Creates `data/backups/galley-YYYYMMDD-HHMMSS/` containing:
- `galley.sqlite` — database
- `media/` — media assets
- `imports/` — raw source files
- `env.bak` — config snapshot (reference only)
- `BACKUP_INFO.txt` — timestamp, hostname, contents

### Database-only backup

```bash
make backup-db
```

Same as above but skips `media/` and `imports/`. Faster when only the database has changed.

### List available backups

```bash
make backup-list
```

### Database backup safety

The backup script uses `sqlite3 .backup` when sqlite3 is installed. This command performs an online backup that is safe while the application is running.

If sqlite3 is not available, the script falls back to `cp`. In that case:
- Stop the application before backing up to avoid capturing a partial write
- `make down && make backup && make up`

### Running backups regularly

There is no automatic scheduled backup. Run `make backup` before:
- making significant changes to the archive
- updating or rebuilding the application
- changing the database schema

For automated backups, add a cron entry on the host:
```
# Example: daily backup at 2am
0 2 * * * cd /path/to/galley && bash scripts/backup/backup.sh >> data/logs/backup.log 2>&1
```

---

## Restore

### Before restoring

1. Stop the application: `make down`
2. Consider backing up the current state first: `make backup`
3. Know which backup you want: `make backup-list`

### Full restore

```bash
make restore BACKUP=data/backups/galley-YYYYMMDD-HHMMSS
```

The restore script will:
1. Show what will be overwritten
2. Warn if current data exists
3. Ask for confirmation before proceeding
4. Restore database, media, and imports from the backup

After restore, restart the application:
```bash
make up
```

### Database-only restore

If a backup contains only a database (created with `make backup-db`), the restore script will only restore the database — it skips media and imports automatically because they are not in the backup.

### Manual restore

The backup is a plain directory. You can restore any part of it manually:

```bash
# Restore only the database
cp data/backups/galley-YYYYMMDD-HHMMSS/galley.sqlite data/db/galley.sqlite

# Restore only media
rm -rf data/media && cp -r data/backups/galley-YYYYMMDD-HHMMSS/media data/media
```

### Restore to a different machine

1. Copy the backup directory to the new machine (USB, LAN copy, etc.)
2. Clone or copy the repo to the new machine
3. Copy `.env.example` to `.env` and configure for the new machine
4. Run `make restore BACKUP=/path/to/galley-YYYYMMDD-HHMMSS`
5. Run `make up`

If the data directory path is different on the new machine, update `DATABASE_URL` and related paths in `.env`.

---

## Retention

### Naming convention

All backups are named `galley-YYYYMMDD-HHMMSS`. Sorting alphabetically gives chronological order.

### Pruning old backups

```bash
make backup-prune            # remove backups older than 30 days
make backup-prune KEEP_DAYS=14   # keep last 14 days
```

Pruning removes directories from `data/backups/` that are older than the threshold. It does not touch the current day's backups.

**Pruning is manual.** It does not run automatically.

### Inspecting a backup

```bash
cat data/backups/galley-YYYYMMDD-HHMMSS/BACKUP_INFO.txt
ls  data/backups/galley-YYYYMMDD-HHMMSS/
```

The backup directory is a plain filesystem tree — you can open, copy, or inspect any file inside it directly.

---

## Safety rules

- Restore always shows a plan before acting
- Restore warns if existing data would be overwritten
- Restore requires confirmation (`[y/N]`) unless `GALLEY_RESTORE_YES=1` is set
- Restore fails immediately if the backup directory does not exist
- Restore fails if the backup directory contains no recognizable items
- `.env` is never automatically restored — review `env.bak` in the backup and apply changes manually
- `make clean` removes Docker containers and images only — it does **not** touch `data/`
- Pruning only removes directories matching the `galley-*` pattern inside `data/backups/`

---

## Troubleshooting

**Restore says "no restorable items"**
The backup directory exists but does not contain `galley.sqlite`, `media/`, or `imports/`. The backup may be incomplete. Check `BACKUP_INFO.txt`.

**Database appears empty after restore**
Check that the restore completed without error. Verify `data/db/galley.sqlite` exists and is not zero bytes. Restart the application with `make restart`.

**Media or imports missing after restore**
If the backup was created with `make backup-db`, media and imports were not included. Use a full backup for a complete restore.

**sqlite3 not found warning**
Install sqlite3 (`apt install sqlite3` / `brew install sqlite3`) for safer live database backups. Without it, the backup script uses `cp` which is less safe with a running database.

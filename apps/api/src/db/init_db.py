"""
Simple SQL-file migration runner.

Reads .sql files from the migrations/ directory in version order,
checks which have already been applied via schema_migrations, and
executes any pending ones inside a single transaction per file.
"""

import logging
import sqlite3
from pathlib import Path

from src.config.settings import settings

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _get_conn() -> sqlite3.Connection:
    db_path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = _get_conn()
    try:
        # Bootstrap migrations table if it doesn't exist yet
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version     TEXT PRIMARY KEY,
                applied_at  TEXT NOT NULL,
                description TEXT
            )
        """)
        conn.commit()

        applied = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }

        migration_files = sorted(
            f for f in MIGRATIONS_DIR.glob("*.sql")
            if not f.name.endswith(".rollback.sql")
        )
        if not migration_files:
            logger.warning("No migration files found in %s", MIGRATIONS_DIR)
            return

        for migration_file in migration_files:
            version = migration_file.stem.split("_")[0]  # e.g. "001" from "001_initial_schema"
            if version in applied:
                logger.debug("Migration %s already applied — skipping", version)
                continue

            logger.info("Applying migration %s (%s)", version, migration_file.name)
            sql = migration_file.read_text(encoding="utf-8")

            # executescript commits any pending transaction and runs the script
            conn.executescript(sql)

            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at, description) "
                "VALUES (?, datetime('now'), ?)",
                (version, migration_file.stem),
            )
            conn.commit()
            logger.info("Migration %s applied", version)

    finally:
        conn.close()

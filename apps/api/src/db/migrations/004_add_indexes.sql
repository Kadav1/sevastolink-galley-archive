-- Migration 004: Add indexes for common query paths
--
-- The default library view filters by archived and sorts by updated_at DESC.
-- Without these indexes SQLite full-scans the recipes table on every page load.

CREATE INDEX IF NOT EXISTS idx_recipes_archived_updated
    ON recipes (archived, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_recipes_updated_at
    ON recipes (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_recipes_last_cooked_at
    ON recipes (last_cooked_at DESC);

CREATE INDEX IF NOT EXISTS idx_recipes_archived
    ON recipes (archived);

-- Rollback for migration 004: drop the indexes added for common query paths.

DROP INDEX IF EXISTS idx_recipes_archived_updated;
DROP INDEX IF EXISTS idx_recipes_updated_at;
DROP INDEX IF EXISTS idx_recipes_last_cooked_at;
DROP INDEX IF EXISTS idx_recipes_archived;

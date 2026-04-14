-- Rollback for migration 002: remove cover_media_asset_id from recipes.
-- Requires SQLite 3.35.0+ (ALTER TABLE ... DROP COLUMN support).

ALTER TABLE recipes DROP COLUMN cover_media_asset_id;

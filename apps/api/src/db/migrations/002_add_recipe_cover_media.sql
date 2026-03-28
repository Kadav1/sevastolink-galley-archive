-- Migration 002: add cover_media_asset_id to recipes
-- Allows attaching a cover image to a canonical recipe.

ALTER TABLE recipes ADD COLUMN cover_media_asset_id TEXT REFERENCES media_assets(id) ON DELETE SET NULL;

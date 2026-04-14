-- Rollback for migration 001: drop all tables created by the initial schema.
-- WARNING: This destroys all data. Take a backup before running.

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS recipe_fts;
DROP TABLE IF EXISTS recipe_notes;
DROP TABLE IF EXISTS recipe_sources;
DROP TABLE IF EXISTS recipe_steps;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS structured_candidates;
DROP TABLE IF EXISTS intake_jobs;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS media_assets;
DROP TABLE IF EXISTS app_settings;

PRAGMA foreign_keys = ON;

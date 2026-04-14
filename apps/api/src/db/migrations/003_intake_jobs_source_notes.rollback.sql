-- Rollback for migration 003: remove source_notes from intake_jobs.
-- Requires SQLite 3.35.0+ (ALTER TABLE ... DROP COLUMN support).

ALTER TABLE intake_jobs DROP COLUMN source_notes;

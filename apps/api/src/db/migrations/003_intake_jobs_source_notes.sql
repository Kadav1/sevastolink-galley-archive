-- Migration 003: Add source_notes to intake_jobs
-- Stores free-text context notes captured at intake job creation time.
-- Previously this field was accepted by IntakeJobCreate but silently dropped.

ALTER TABLE intake_jobs ADD COLUMN source_notes TEXT;

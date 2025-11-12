-- Add explanation column to signals table for LLM-generated natural language explanations
-- Migration: 001_add_explanation_column
-- Date: 2025-11-12

ALTER TABLE signals
ADD COLUMN IF NOT EXISTS explanation TEXT;

COMMENT ON COLUMN signals.explanation IS 'LLM-generated natural language explanation of the signal (optional, 2 paragraphs max)';

-- ========================================
-- KaliRoot CLI - Add Geolocation Columns
-- ========================================
-- Run this in your Supabase SQL Editor to add geolocation fields

-- Add geolocation columns to cli_sessions
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS country TEXT;
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS country_code TEXT;
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS region TEXT;
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS city TEXT;
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS latitude DECIMAL(10,6);
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS longitude DECIMAL(10,6);
ALTER TABLE cli_sessions ADD COLUMN IF NOT EXISTS isp TEXT;

-- Create index for country lookups
CREATE INDEX IF NOT EXISTS idx_cli_sessions_country ON cli_sessions(country);
CREATE INDEX IF NOT EXISTS idx_cli_sessions_city ON cli_sessions(city);

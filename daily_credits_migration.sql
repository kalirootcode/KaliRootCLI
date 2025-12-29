-- ═══════════════════════════════════════════════════════════════════════════════
-- DAILY CREDITS SYSTEM MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════════
-- This migration adds support for daily credits reset for all users
-- Users will receive 20 credits daily when they reach 0 or after 24 hours

-- Add column to track last daily credits reset
ALTER TABLE cli_users 
ADD COLUMN IF NOT EXISTS daily_credits_reset_date TIMESTAMP WITH TIME ZONE;

-- Initialize existing users with current timestamp
UPDATE cli_users 
SET daily_credits_reset_date = NOW() 
WHERE daily_credits_reset_date IS NULL;

-- Give 20 credits to users who currently have 0
UPDATE cli_users 
SET credit_balance = 20,
    daily_credits_reset_date = NOW()
WHERE credit_balance = 0;

-- ═══════════════════════════════════════════════════════════════════════════════
-- NOTES:
-- - All users (FREE and PREMIUM) get 20 daily credits
-- - Credits reset when user reaches 0 OR after 24 hours
-- - If user has > 20 credits (purchased), no reset until they reach 0
-- ═══════════════════════════════════════════════════════════════════════════════

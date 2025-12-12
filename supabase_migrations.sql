-- ========================================
-- KaliRoot CLI - Supabase Migrations
-- ========================================
-- Run this in your Supabase SQL Editor

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ========================================
-- Table: cli_users
-- ========================================
CREATE TABLE IF NOT EXISTS cli_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    credit_balance INTEGER DEFAULT 5,
    subscription_status TEXT DEFAULT 'free',  -- 'free', 'pending', 'premium'
    subscription_expiry_date TIMESTAMPTZ,
    nowpayments_invoice_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Index for username lookups
CREATE INDEX IF NOT EXISTS idx_cli_users_username ON cli_users(username);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_cli_users_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cli_users_updated_at ON cli_users;
CREATE TRIGGER trg_cli_users_updated_at
    BEFORE UPDATE ON cli_users
    FOR EACH ROW
    EXECUTE FUNCTION update_cli_users_timestamp();

-- ========================================
-- Table: cli_chat_history
-- ========================================
CREATE TABLE IF NOT EXISTS cli_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cli_chat_history_user ON cli_chat_history(user_id);

-- ========================================
-- Function: register_cli_user
-- ========================================
CREATE OR REPLACE FUNCTION register_cli_user(
    p_username TEXT,
    p_password_hash TEXT,
    p_initial_credits INTEGER DEFAULT 5
)
RETURNS TABLE(id UUID, username TEXT) AS $$
DECLARE
    new_id UUID;
    new_username TEXT;
BEGIN
    INSERT INTO cli_users (username, password_hash, credit_balance)
    VALUES (p_username, p_password_hash, p_initial_credits)
    RETURNING cli_users.id, cli_users.username INTO new_id, new_username;
    
    RETURN QUERY SELECT new_id, new_username;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Username already exists';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: get_cli_user_by_username
-- ========================================
CREATE OR REPLACE FUNCTION get_cli_user_by_username(p_username TEXT)
RETURNS TABLE(
    id UUID,
    username TEXT,
    password_hash TEXT,
    credit_balance INTEGER,
    subscription_status TEXT,
    subscription_expiry_date TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.username,
        u.password_hash,
        u.credit_balance,
        u.subscription_status,
        u.subscription_expiry_date
    FROM cli_users u
    WHERE u.username = p_username;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: deduct_cli_credit
-- ========================================
CREATE OR REPLACE FUNCTION deduct_cli_credit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    current_balance INTEGER;
    is_premium BOOLEAN;
BEGIN
    SELECT credit_balance, (subscription_status = 'premium' AND subscription_expiry_date > now())
    INTO current_balance, is_premium
    FROM cli_users 
    WHERE id = p_user_id 
    FOR UPDATE;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Premium users don't consume credits
    IF is_premium THEN
        RETURN TRUE;
    END IF;
    
    IF current_balance <= 0 THEN
        RETURN FALSE;
    END IF;
    
    UPDATE cli_users SET credit_balance = credit_balance - 1 WHERE id = p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: add_cli_credits
-- ========================================
CREATE OR REPLACE FUNCTION add_cli_credits(p_user_id UUID, p_amount INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cli_users 
    SET credit_balance = credit_balance + p_amount,
        updated_at = now()
    WHERE id = p_user_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: activate_cli_subscription
-- ========================================
CREATE OR REPLACE FUNCTION activate_cli_subscription(
    p_user_id UUID,
    p_invoice_id TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cli_users
    SET subscription_status = 'premium',
        subscription_expiry_date = now() + INTERVAL '30 days',
        nowpayments_invoice_id = p_invoice_id,
        credit_balance = credit_balance + 250,  -- Bonus credits
        updated_at = now()
    WHERE id = p_user_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: set_cli_subscription_pending
-- ========================================
CREATE OR REPLACE FUNCTION set_cli_subscription_pending(
    p_user_id UUID,
    p_invoice_id TEXT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cli_users
    SET subscription_status = 'pending',
        nowpayments_invoice_id = p_invoice_id,
        updated_at = now()
    WHERE id = p_user_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: check_cli_subscription
-- ========================================
CREATE OR REPLACE FUNCTION check_cli_subscription(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    status TEXT;
    expiry TIMESTAMPTZ;
BEGIN
    SELECT subscription_status, subscription_expiry_date
    INTO status, expiry
    FROM cli_users
    WHERE id = p_user_id;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Check if premium and not expired
    IF status = 'premium' AND expiry > now() THEN
        RETURN TRUE;
    END IF;
    
    -- If expired, update status
    IF status = 'premium' AND expiry <= now() THEN
        UPDATE cli_users
        SET subscription_status = 'free'
        WHERE id = p_user_id;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- RLS Policies (optional, for security)
-- ========================================
ALTER TABLE cli_users ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role has full access"
    ON cli_users
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Public can only read their own data (via RPC)
DROP POLICY IF EXISTS allow_public_select_cli_users ON cli_users;
CREATE POLICY allow_public_select_cli_users ON cli_users
    FOR SELECT
    USING (true);

-- Deny direct inserts from anon (use RPC instead)
DROP POLICY IF EXISTS deny_public_insert_cli_users ON cli_users;
CREATE POLICY deny_public_insert_cli_users ON cli_users
    FOR INSERT
    WITH CHECK (false);

-- ========================================
-- Audit table (optional)
-- ========================================
CREATE TABLE IF NOT EXISTS cli_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id),
    event_type TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_cli_audit(
    p_user_id UUID,
    p_event_type TEXT,
    p_details JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO cli_audit_log (user_id, event_type, details)
    VALUES (p_user_id, p_event_type, p_details);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

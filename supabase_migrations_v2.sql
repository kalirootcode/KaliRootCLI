-- ========================================
-- KaliRoot CLI v2.0 - Supabase Migrations
-- ========================================
-- Run this in your Supabase SQL Editor
-- This version uses Supabase Auth for email verification

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ========================================
-- Table: cli_users (linked to auth.users)
-- ========================================
DROP TABLE IF EXISTS cli_users CASCADE;

CREATE TABLE cli_users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    credit_balance INTEGER DEFAULT 5,
    subscription_status TEXT DEFAULT 'free' CHECK (subscription_status IN ('free', 'pending', 'premium')),
    subscription_expiry_date TIMESTAMPTZ,
    current_invoice_id TEXT,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_cli_users_email ON cli_users(email);
CREATE INDEX IF NOT EXISTS idx_cli_users_username ON cli_users(username);
CREATE INDEX IF NOT EXISTS idx_cli_users_invoice ON cli_users(current_invoice_id);

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
-- Table: cli_payments (payment history)
-- ========================================
CREATE TABLE IF NOT EXISTS cli_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    invoice_id TEXT NOT NULL,
    payment_id TEXT,
    amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USDT',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirming', 'confirmed', 'finished', 'failed', 'expired')),
    payment_type TEXT DEFAULT 'subscription' CHECK (payment_type IN ('subscription', 'credits')),
    nowpayments_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cli_payments_user ON cli_payments(user_id);
CREATE INDEX IF NOT EXISTS idx_cli_payments_invoice ON cli_payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_cli_payments_status ON cli_payments(status);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trg_cli_payments_updated_at ON cli_payments;
CREATE TRIGGER trg_cli_payments_updated_at
    BEFORE UPDATE ON cli_payments
    FOR EACH ROW
    EXECUTE FUNCTION update_cli_users_timestamp();

-- ========================================
-- Table: cli_chat_history
-- ========================================
CREATE TABLE IF NOT EXISTS cli_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cli_chat_history_user ON cli_chat_history(user_id);

-- ========================================
-- Function: Auto-create cli_user on signup
-- ========================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cli_users (id, email, username, credit_balance)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'username', SPLIT_PART(NEW.email, '@', 1)),
        5
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to auto-create user profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- ========================================
-- Function: Create payment record
-- ========================================
CREATE OR REPLACE FUNCTION create_payment(
    p_user_id UUID,
    p_invoice_id TEXT,
    p_amount DECIMAL,
    p_payment_type TEXT DEFAULT 'subscription'
)
RETURNS UUID AS $$
DECLARE
    payment_id UUID;
BEGIN
    INSERT INTO cli_payments (user_id, invoice_id, amount, payment_type)
    VALUES (p_user_id, p_invoice_id, p_amount, p_payment_type)
    RETURNING id INTO payment_id;
    
    -- Update user's current invoice
    UPDATE cli_users 
    SET current_invoice_id = p_invoice_id,
        subscription_status = CASE 
            WHEN subscription_status = 'free' THEN 'pending'
            ELSE subscription_status
        END
    WHERE id = p_user_id;
    
    RETURN payment_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: Process successful payment
-- ========================================
CREATE OR REPLACE FUNCTION process_payment_success(
    p_invoice_id TEXT,
    p_payment_id TEXT,
    p_nowpayments_data JSONB DEFAULT '{}'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_user_id UUID;
    v_payment_type TEXT;
    v_amount DECIMAL;
BEGIN
    -- Find the payment record
    SELECT user_id, payment_type, amount INTO v_user_id, v_payment_type, v_amount
    FROM cli_payments
    WHERE invoice_id = p_invoice_id AND status = 'pending'
    LIMIT 1;
    
    IF v_user_id IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Update payment status
    UPDATE cli_payments
    SET status = 'finished',
        payment_id = p_payment_id,
        nowpayments_data = p_nowpayments_data,
        updated_at = now()
    WHERE invoice_id = p_invoice_id;
    
    -- Process based on payment type
    IF v_payment_type = 'subscription' THEN
        -- Activate subscription + bonus credits
        UPDATE cli_users
        SET subscription_status = 'premium',
            subscription_expiry_date = now() + INTERVAL '30 days',
            credit_balance = credit_balance + 250,
            total_spent = total_spent + v_amount,
            current_invoice_id = NULL
        WHERE id = v_user_id;
    ELSIF v_payment_type = 'credits' THEN
        -- Add credits based on amount ($1 = 10 credits)
        UPDATE cli_users
        SET credit_balance = credit_balance + (v_amount * 10)::INTEGER,
            total_spent = total_spent + v_amount,
            current_invoice_id = NULL
        WHERE id = v_user_id;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: Check and refresh subscription
-- ========================================
CREATE OR REPLACE FUNCTION check_subscription(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_status TEXT;
    v_expiry TIMESTAMPTZ;
BEGIN
    SELECT subscription_status, subscription_expiry_date INTO v_status, v_expiry
    FROM cli_users WHERE id = p_user_id;
    
    IF v_status = 'premium' AND v_expiry > now() THEN
        RETURN TRUE;
    END IF;
    
    -- Expired, update to free
    IF v_status = 'premium' AND v_expiry <= now() THEN
        UPDATE cli_users SET subscription_status = 'free' WHERE id = p_user_id;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: Deduct credit
-- ========================================
CREATE OR REPLACE FUNCTION deduct_credit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_credits INTEGER;
    v_is_premium BOOLEAN;
BEGIN
    -- Check subscription first
    SELECT check_subscription(p_user_id) INTO v_is_premium;
    IF v_is_premium THEN
        RETURN TRUE;  -- Premium users don't use credits
    END IF;
    
    SELECT credit_balance INTO v_credits FROM cli_users WHERE id = p_user_id FOR UPDATE;
    
    IF v_credits <= 0 THEN
        RETURN FALSE;
    END IF;
    
    UPDATE cli_users SET credit_balance = credit_balance - 1 WHERE id = p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: Get user stats
-- ========================================
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS TABLE(
    credits INTEGER,
    is_premium BOOLEAN,
    days_left INTEGER,
    total_queries BIGINT,
    total_spent DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.credit_balance,
        (u.subscription_status = 'premium' AND u.subscription_expiry_date > now()),
        CASE 
            WHEN u.subscription_status = 'premium' AND u.subscription_expiry_date > now()
            THEN EXTRACT(DAY FROM u.subscription_expiry_date - now())::INTEGER
            ELSE 0
        END,
        (SELECT COUNT(*) FROM cli_chat_history WHERE user_id = p_user_id AND role = 'user'),
        u.total_spent
    FROM cli_users u
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- RLS Policies
-- ========================================
ALTER TABLE cli_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cli_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE cli_chat_history ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON cli_users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON cli_users
    FOR UPDATE USING (auth.uid() = id);

-- Payments: users see own, service role can insert/update
CREATE POLICY "Users can view own payments" ON cli_payments
    FOR SELECT USING (auth.uid() = user_id);

-- Chat history
CREATE POLICY "Users can view own chat" ON cli_chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat" ON cli_chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ========================================
-- Audit logging
-- ========================================
CREATE TABLE IF NOT EXISTS cli_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id),
    event_type TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON cli_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_event ON cli_audit_log(event_type);

-- Grant necessary permissions
GRANT ALL ON cli_users TO service_role;
GRANT ALL ON cli_payments TO service_role;
GRANT ALL ON cli_chat_history TO service_role;
GRANT ALL ON cli_audit_log TO service_role;

-- ========================================
-- KR-CLI Web Platform - Database Migrations
-- ========================================
-- Run this in your Supabase SQL Editor
-- These tables support the web platform and admin panel

-- ========================================
-- Table: admin_users (Admin Panel Access)
-- ========================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT DEFAULT 'Admin',
    role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'superadmin')),
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create default admin (change password after first login!)
-- Password: krcli_admin_2026 (hashed with bcrypt)
INSERT INTO admin_users (email, password_hash, name, role) 
VALUES ('admin@kr-clidn.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4/VkWjDlwPjpNu.W', 'RK13', 'superadmin')
ON CONFLICT (email) DO NOTHING;

-- ========================================
-- Table: support_tickets
-- ========================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE SET NULL,
    user_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_to UUID REFERENCES admin_users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);

-- ========================================
-- Table: support_messages (Chat Messages)
-- ========================================
CREATE TABLE IF NOT EXISTS support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'admin')),
    sender_id UUID,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON support_messages(ticket_id);

-- ========================================
-- Table: web_sessions (Track CLI-to-Web Sessions)
-- ========================================
CREATE TABLE IF NOT EXISTS web_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    device_type TEXT DEFAULT 'desktop',
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ DEFAULT (now() + INTERVAL '24 hours'),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_web_sessions_user ON web_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_web_sessions_token ON web_sessions(session_token);

-- ========================================
-- Table: web_activity_log (User Activity Tracking)
-- ========================================
CREATE TABLE IF NOT EXISTS web_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    page_visited TEXT,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_web_activity_user ON web_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_web_activity_action ON web_activity_log(action);
CREATE INDEX IF NOT EXISTS idx_web_activity_date ON web_activity_log(created_at);

-- ========================================
-- RLS Policies for New Tables
-- ========================================
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE web_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE web_activity_log ENABLE ROW LEVEL SECURITY;

-- Users can see their own tickets
CREATE POLICY "Users can view own tickets" ON support_tickets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create tickets" ON support_tickets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can see messages on their tickets
CREATE POLICY "Users can view ticket messages" ON support_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM support_tickets 
            WHERE support_tickets.id = support_messages.ticket_id 
            AND support_tickets.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can send messages" ON support_messages
    FOR INSERT WITH CHECK (sender_type = 'user' AND sender_id = auth.uid());

-- Web sessions
CREATE POLICY "Users can view own web sessions" ON web_sessions
    FOR SELECT USING (auth.uid() = user_id);

-- Grant service role access
GRANT ALL ON admin_users TO service_role;
GRANT ALL ON support_tickets TO service_role;
GRANT ALL ON support_messages TO service_role;
GRANT ALL ON web_sessions TO service_role;
GRANT ALL ON web_activity_log TO service_role;

-- ========================================
-- Helper Functions
-- ========================================

-- Function to get user analytics
CREATE OR REPLACE FUNCTION get_admin_analytics()
RETURNS TABLE(
    total_users BIGINT,
    active_users BIGINT,
    premium_users BIGINT,
    free_users BIGINT,
    total_credits BIGINT,
    open_tickets BIGINT,
    total_revenue DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM cli_users) as total_users,
        (SELECT COUNT(*) FROM cli_users WHERE updated_at > now() - INTERVAL '30 days') as active_users,
        (SELECT COUNT(*) FROM cli_users WHERE subscription_status = 'premium' AND subscription_expiry_date > now()) as premium_users,
        (SELECT COUNT(*) FROM cli_users WHERE subscription_status = 'free') as free_users,
        (SELECT COALESCE(SUM(credit_balance), 0) FROM cli_users) as total_credits,
        (SELECT COUNT(*) FROM support_tickets WHERE status = 'open') as open_tickets,
        (SELECT COALESCE(SUM(total_spent), 0) FROM cli_users) as total_revenue;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute
GRANT EXECUTE ON FUNCTION get_admin_analytics() TO service_role;

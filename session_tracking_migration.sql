-- ========================================
-- KaliRoot CLI - Session Tracking Migration
-- ========================================
-- Run this in your Supabase SQL Editor

-- ========================================
-- Table: cli_sessions
-- Tracks all user login sessions with system info
-- ========================================
CREATE TABLE IF NOT EXISTS cli_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    
    -- Network Info
    public_ip TEXT,
    local_ip TEXT,
    is_vpn BOOLEAN DEFAULT FALSE,
    vpn_interface TEXT,
    
    -- System Info
    hostname TEXT,
    os_name TEXT,
    os_version TEXT,
    kernel_version TEXT,
    cpu_model TEXT,
    cpu_cores INTEGER,
    ram_total_gb DECIMAL(5,2),
    disk_total_gb DECIMAL(8,2),
    
    -- Environment
    distro TEXT,
    shell TEXT,
    terminal TEXT,
    timezone TEXT,
    locale TEXT,
    python_version TEXT,
    screen_resolution TEXT,
    
    -- Fingerprint (non-reversible hash)
    machine_fingerprint TEXT,
    
    -- Timestamps
    session_start TIMESTAMPTZ DEFAULT now(),
    last_activity TIMESTAMPTZ DEFAULT now()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_cli_sessions_user ON cli_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_cli_sessions_start ON cli_sessions(session_start DESC);
CREATE INDEX IF NOT EXISTS idx_cli_sessions_ip ON cli_sessions(public_ip);

-- ========================================
-- Function: log_cli_session
-- Registers a new session with full system info
-- ========================================
CREATE OR REPLACE FUNCTION log_cli_session(
    p_user_id UUID,
    p_public_ip TEXT DEFAULT NULL,
    p_local_ip TEXT DEFAULT NULL,
    p_is_vpn BOOLEAN DEFAULT FALSE,
    p_vpn_interface TEXT DEFAULT NULL,
    p_hostname TEXT DEFAULT NULL,
    p_os_name TEXT DEFAULT NULL,
    p_os_version TEXT DEFAULT NULL,
    p_kernel_version TEXT DEFAULT NULL,
    p_cpu_model TEXT DEFAULT NULL,
    p_cpu_cores INTEGER DEFAULT NULL,
    p_ram_total_gb DECIMAL DEFAULT NULL,
    p_disk_total_gb DECIMAL DEFAULT NULL,
    p_distro TEXT DEFAULT NULL,
    p_shell TEXT DEFAULT NULL,
    p_terminal TEXT DEFAULT NULL,
    p_timezone TEXT DEFAULT NULL,
    p_locale TEXT DEFAULT NULL,
    p_python_version TEXT DEFAULT NULL,
    p_screen_resolution TEXT DEFAULT NULL,
    p_machine_fingerprint TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_session_id UUID;
BEGIN
    INSERT INTO cli_sessions (
        user_id, public_ip, local_ip, is_vpn, vpn_interface,
        hostname, os_name, os_version, kernel_version,
        cpu_model, cpu_cores, ram_total_gb, disk_total_gb,
        distro, shell, terminal, timezone, locale,
        python_version, screen_resolution, machine_fingerprint
    ) VALUES (
        p_user_id, p_public_ip, p_local_ip, p_is_vpn, p_vpn_interface,
        p_hostname, p_os_name, p_os_version, p_kernel_version,
        p_cpu_model, p_cpu_cores, p_ram_total_gb, p_disk_total_gb,
        p_distro, p_shell, p_terminal, p_timezone, p_locale,
        p_python_version, p_screen_resolution, p_machine_fingerprint
    )
    RETURNING id INTO new_session_id;
    
    RETURN new_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: update_session_activity
-- Updates last_activity timestamp for a session
-- ========================================
CREATE OR REPLACE FUNCTION update_session_activity(p_session_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE cli_sessions
    SET last_activity = now()
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- Function: get_user_sessions
-- Get recent sessions for a user
-- ========================================
CREATE OR REPLACE FUNCTION get_user_sessions(
    p_user_id UUID,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE(
    session_id UUID,
    public_ip TEXT,
    is_vpn BOOLEAN,
    distro TEXT,
    hostname TEXT,
    session_start TIMESTAMPTZ,
    last_activity TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.public_ip,
        s.is_vpn,
        s.distro,
        s.hostname,
        s.session_start,
        s.last_activity
    FROM cli_sessions s
    WHERE s.user_id = p_user_id
    ORDER BY s.session_start DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- RLS Policies
-- ========================================
ALTER TABLE cli_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Service role has full access to sessions" ON cli_sessions;
CREATE POLICY "Service role has full access to sessions"
    ON cli_sessions
    FOR ALL
    USING (true)
    WITH CHECK (true);

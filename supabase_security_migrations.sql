-- ═══════════════════════════════════════════════════════════════════════════════
-- KR-CLI DOMINION: Security & Usage Logging Schema
-- Run this in your Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════════

-- Usage logging table for rate-limiting and abuse detection
CREATE TABLE IF NOT EXISTS cli_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES cli_users(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,  -- 'ai_query', 'agent_run', 'payment', etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metrics (without storing actual content for privacy)
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    latency_ms INT DEFAULT 0,
    
    -- Abuse detection signals
    is_tty BOOLEAN DEFAULT TRUE,
    client_hash TEXT  -- Non-reversible fingerprint
);

-- Indexes for efficient rate-limit queries
CREATE INDEX IF NOT EXISTS idx_usage_user_time 
ON cli_usage_log (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_usage_action_time 
ON cli_usage_log (action_type, created_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════════
-- RATE LIMIT CHECK FUNCTION
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_action TEXT,
    p_window_minutes INT,
    p_max_count INT
) RETURNS BOOLEAN AS $$
DECLARE
    current_count INT;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM cli_usage_log
    WHERE user_id = p_user_id
      AND action_type = p_action
      AND created_at > NOW() - (p_window_minutes || ' minutes')::INTERVAL;
    
    RETURN current_count < p_max_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ═══════════════════════════════════════════════════════════════════════════════
-- CLEANUP OLD LOGS (Run periodically via pg_cron or manually)
-- Keeps only last 30 days of usage data
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION cleanup_old_usage_logs()
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM cli_usage_log
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ═══════════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY (Users can only see their own logs)
-- ═══════════════════════════════════════════════════════════════════════════════

ALTER TABLE cli_usage_log ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own usage logs
CREATE POLICY "Users can view own usage" ON cli_usage_log
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Service role can insert logs
CREATE POLICY "Service can insert logs" ON cli_usage_log
    FOR INSERT
    WITH CHECK (TRUE);

-- Grant access to authenticated users
GRANT SELECT ON cli_usage_log TO authenticated;
GRANT INSERT ON cli_usage_log TO authenticated;
GRANT EXECUTE ON FUNCTION check_rate_limit TO authenticated;

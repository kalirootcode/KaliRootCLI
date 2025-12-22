"""
Security Module for KaliRoot CLI
Implements rate-limiting, abuse detection, and session protection.

Architecture: Zero Trust - All critical validation happens server-side,
but this module provides client-side UX improvements and early detection.
"""

import sys
import time
import hashlib
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN LIMITS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PLAN_LIMITS = {
    "free": {
        "queries_per_minute": 2,
        "queries_per_hour": 10,
        "queries_per_day": 5,  # Hard cap for FREE
        "agent_per_hour": 0,
        "max_input_tokens": 1000,
        "max_output_tokens": 1500,
        "daily_token_limit": 10000,  # Anti-abuse daily cap
        "cooldown_seconds": 300,  # 5 min
    },
    "starter": {
        "queries_per_minute": 5,
        "queries_per_hour": 60,
        "queries_per_day": 500,  # Based on credits
        "agent_per_hour": 5,
        "max_input_tokens": 2000,
        "max_output_tokens": 3000,
        "daily_token_limit": 100000,
        "cooldown_seconds": 120,  # 2 min
    },
    "hacker_pro": {
        "queries_per_minute": 10,
        "queries_per_hour": 150,
        "queries_per_day": 1200,
        "agent_per_hour": 15,
        "max_input_tokens": 4000,
        "max_output_tokens": 4000,
        "daily_token_limit": 500000,
        "cooldown_seconds": 60,  # 1 min
    },
    "elite": {
        "queries_per_minute": 20,
        "queries_per_hour": 500,
        "queries_per_day": 5000,
        "agent_per_hour": 50,
        "max_input_tokens": 8000,
        "max_output_tokens": 4096,
        "daily_token_limit": 2000000,  # 2M tokens/day
        "cooldown_seconds": 15,  # 15 seg
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT DATACLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityCheckResult:
    """Result of a security check."""
    allowed: bool
    reason: str
    retry_after: Optional[int] = None  # Seconds to wait
    details: Dict = field(default_factory=dict)
    
    def __bool__(self) -> bool:
        return self.allowed


# ═══════════════════════════════════════════════════════════════════════════════
# TTY DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def is_interactive_session() -> bool:
    """
    Check if we're running in an interactive terminal session.
    Non-interactive sessions may indicate automation/scripting.
    
    Returns:
        True if running interactively, False if likely automated
    """
    try:
        # Check if stdin is a TTY
        if not sys.stdin.isatty():
            return False
        
        # Check if stdout is a TTY
        if not sys.stdout.isatty():
            return False
        
        # Check for common automation environment variables
        import os
        automation_vars = ['CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS', 'JENKINS_URL']
        for var in automation_vars:
            if os.environ.get(var):
                return False
        
        return True
    except Exception:
        # In case of any error, assume interactive
        return True


def get_session_fingerprint() -> str:
    """
    Generate a non-reversible fingerprint of the current session.
    Used for abuse detection without storing sensitive data.
    """
    import os
    import platform
    
    components = [
        os.environ.get('TERM', 'unknown'),
        os.environ.get('SHELL', 'unknown'),
        platform.node(),  # Hostname
        str(os.getuid()) if hasattr(os, 'getuid') else 'windows',
    ]
    
    raw = "|".join(components)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════════════════════
# TOKEN BUCKET RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class TokenBucket:
    """
    Token Bucket algorithm for rate limiting.
    Allows bursts while enforcing average limits.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_update = time.time()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.
        
        Returns:
            True if tokens were consumed, False if not enough available
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get seconds to wait before tokens are available."""
        self._refill()
        if self.tokens >= tokens:
            return 0
        needed = tokens - self.tokens
        return needed / self.refill_rate


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDING WINDOW RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for tracking requests over time.
    More accurate than fixed windows for edge cases.
    """
    
    def __init__(self):
        # Store timestamps of requests per user per action
        self._windows: Dict[str, deque] = {}
    
    def _get_key(self, user_id: str, action: str) -> str:
        return f"{user_id}:{action}"
    
    def check(self, user_id: str, action: str, limit: int, window_seconds: int) -> bool:
        """
        Check if action is allowed within rate limit.
        
        Args:
            user_id: User identifier
            action: Action type (e.g., 'ai_query', 'agent_run')
            limit: Maximum allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if allowed, False if rate limited
        """
        key = self._get_key(user_id, action)
        now = time.time()
        cutoff = now - window_seconds
        
        if key not in self._windows:
            self._windows[key] = deque()
        
        window = self._windows[key]
        
        # Remove expired entries
        while window and window[0] < cutoff:
            window.popleft()
        
        # Check limit
        if len(window) >= limit:
            return False
        
        # Record this request
        window.append(now)
        return True
    
    def get_remaining(self, user_id: str, action: str, limit: int, window_seconds: int) -> int:
        """Get remaining requests in current window."""
        key = self._get_key(user_id, action)
        now = time.time()
        cutoff = now - window_seconds
        
        if key not in self._windows:
            return limit
        
        window = self._windows[key]
        
        # Count non-expired entries
        current_count = sum(1 for t in window if t >= cutoff)
        return max(0, limit - current_count)
    
    def get_reset_time(self, user_id: str, action: str, window_seconds: int) -> int:
        """Get seconds until oldest entry expires."""
        key = self._get_key(user_id, action)
        
        if key not in self._windows or not self._windows[key]:
            return 0
        
        oldest = self._windows[key][0]
        reset_at = oldest + window_seconds
        return max(0, int(reset_at - time.time()))


# ═══════════════════════════════════════════════════════════════════════════════
# ABUSE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

class AbuseDetector:
    """
    Detects patterns indicating automated abuse.
    Calculates a risk score based on multiple signals.
    """
    
    def __init__(self):
        self._query_history: Dict[str, deque] = {}  # user_id -> recent queries
        self._timing_history: Dict[str, deque] = {}  # user_id -> request timestamps
    
    def record_query(self, user_id: str, query: str):
        """Record a query for pattern analysis."""
        now = time.time()
        
        # Initialize if needed
        if user_id not in self._query_history:
            self._query_history[user_id] = deque(maxlen=20)
            self._timing_history[user_id] = deque(maxlen=20)
        
        self._query_history[user_id].append(query)
        self._timing_history[user_id].append(now)
    
    def calculate_risk_score(self, user_id: str) -> Dict:
        """
        Calculate abuse risk score for a user.
        
        Returns:
            Dict with 'score' (0.0-1.0) and 'signals' breakdown
        """
        signals = {
            "is_tty": is_interactive_session(),
            "rapid_fire": False,
            "identical_queries": False,
            "regular_intervals": False,
        }
        
        risk_score = 0.0
        
        # Non-TTY is a strong signal
        if not signals["is_tty"]:
            risk_score += 0.4
        
        # Check timing patterns
        if user_id in self._timing_history:
            timestamps = list(self._timing_history[user_id])
            
            if len(timestamps) >= 3:
                # Calculate intervals
                intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                avg_interval = sum(intervals) / len(intervals)
                
                # Rapid fire: average interval < 2 seconds
                if avg_interval < 2.0:
                    signals["rapid_fire"] = True
                    risk_score += 0.3
                
                # Suspiciously regular intervals (variance < 0.5 seconds)
                if len(intervals) >= 3:
                    variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
                    if variance < 0.5 and avg_interval < 10:
                        signals["regular_intervals"] = True
                        risk_score += 0.2
        
        # Check query patterns
        if user_id in self._query_history:
            queries = list(self._query_history[user_id])
            
            if len(queries) >= 5:
                # Many identical queries
                unique_ratio = len(set(queries)) / len(queries)
                if unique_ratio < 0.3:
                    signals["identical_queries"] = True
                    risk_score += 0.2
        
        return {
            "score": min(risk_score, 1.0),
            "signals": signals,
            "threshold": 0.7,  # Scores above this are flagged
            "flagged": risk_score >= 0.7
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SECURITY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class SecurityManager:
    """
    Central security manager for KR-CLI.
    Coordinates rate limiting, abuse detection, and access control.
    """
    
    def __init__(self):
        self.rate_limiter = SlidingWindowRateLimiter()
        self.abuse_detector = AbuseDetector()
        self._cooldowns: Dict[str, float] = {}  # user_id -> cooldown_until timestamp
    
    def check_access(
        self, 
        user_id: str, 
        plan: str, 
        action: str = "ai_query",
        query: str = ""
    ) -> SecurityCheckResult:
        """
        Perform all security checks for an action.
        
        Args:
            user_id: User identifier
            plan: User's plan (free, starter, hacker_pro, elite)
            action: Type of action being performed
            query: The query being made (for abuse detection)
        
        Returns:
            SecurityCheckResult with allowed status and details
        """
        plan = plan.lower()
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        
        # 1. Check cooldown
        if user_id in self._cooldowns:
            if time.time() < self._cooldowns[user_id]:
                remaining = int(self._cooldowns[user_id] - time.time())
                return SecurityCheckResult(
                    allowed=False,
                    reason="cooldown_active",
                    retry_after=remaining,
                    details={"message": f"Cooldown activo. Espera {remaining} segundos."}
                )
            else:
                del self._cooldowns[user_id]
        
        # 2. Check rate limit per minute
        if not self.rate_limiter.check(user_id, f"{action}_minute", limits["queries_per_minute"], 60):
            retry = self.rate_limiter.get_reset_time(user_id, f"{action}_minute", 60)
            return SecurityCheckResult(
                allowed=False,
                reason="rate_limit_minute",
                retry_after=retry,
                details={
                    "message": f"Límite por minuto alcanzado ({limits['queries_per_minute']}/min).",
                    "remaining": 0,
                    "limit": limits["queries_per_minute"]
                }
            )
        
        # 3. Check rate limit per hour
        if not self.rate_limiter.check(user_id, f"{action}_hour", limits["queries_per_hour"], 3600):
            retry = self.rate_limiter.get_reset_time(user_id, f"{action}_hour", 3600)
            return SecurityCheckResult(
                allowed=False,
                reason="rate_limit_hour",
                retry_after=retry,
                details={
                    "message": f"Límite por hora alcanzado ({limits['queries_per_hour']}/hora).",
                    "remaining": 0,
                    "limit": limits["queries_per_hour"]
                }
            )
        
        # 4. Check abuse patterns (record query first)
        if query:
            self.abuse_detector.record_query(user_id, query)
        
        abuse_result = self.abuse_detector.calculate_risk_score(user_id)
        if abuse_result["flagged"]:
            # Apply cooldown
            cooldown = limits["cooldown_seconds"]
            self._cooldowns[user_id] = time.time() + cooldown
            
            return SecurityCheckResult(
                allowed=False,
                reason="abuse_detected",
                retry_after=cooldown,
                details={
                    "message": "Actividad inusual detectada. Por seguridad, espera antes de continuar.",
                    "risk_score": abuse_result["score"],
                    "signals": abuse_result["signals"]
                }
            )
        
        # 5. Check TTY for sensitive actions (warning only, not blocking)
        is_tty = is_interactive_session()
        
        # 6. All checks passed
        remaining_minute = self.rate_limiter.get_remaining(
            user_id, f"{action}_minute", limits["queries_per_minute"], 60
        )
        remaining_hour = self.rate_limiter.get_remaining(
            user_id, f"{action}_hour", limits["queries_per_hour"], 3600
        )
        
        return SecurityCheckResult(
            allowed=True,
            reason="allowed",
            details={
                "remaining_minute": remaining_minute,
                "remaining_hour": remaining_hour,
                "is_interactive": is_tty,
                "plan": plan
            }
        )
    
    def get_status(self, user_id: str, plan: str) -> Dict:
        """Get current rate limit status for display."""
        plan = plan.lower()
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        
        return {
            "plan": plan,
            "limits": limits,
            "remaining_minute": self.rate_limiter.get_remaining(
                user_id, "ai_query_minute", limits["queries_per_minute"], 60
            ),
            "remaining_hour": self.rate_limiter.get_remaining(
                user_id, "ai_query_hour", limits["queries_per_hour"], 3600
            ),
            "is_interactive": is_interactive_session(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

# Singleton instance for use across the application
security_manager = SecurityManager()


# ═══════════════════════════════════════════════════════════════════════════════
# UX-FRIENDLY ERROR MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def get_rate_limit_message(result: SecurityCheckResult) -> str:
    """Generate a user-friendly message for rate limit errors."""
    reason = result.reason
    details = result.details
    retry = result.retry_after or 0
    
    if reason == "rate_limit_minute":
        return (
            f"⏳ [yellow]Límite por minuto alcanzado[/yellow]\n"
            f"   Disponible en: {retry} segundos\n"
            f"   💡 [dim]Tip: Los planes superiores tienen límites más altos.[/dim]"
        )
    
    elif reason == "rate_limit_hour":
        minutes = retry // 60
        seconds = retry % 60
        return (
            f"📊 [yellow]Límite por hora alcanzado[/yellow]\n"
            f"   Reset en: {minutes}m {seconds}s\n"
            f"   💎 [dim]Actualiza a ELITE para 300 consultas/hora.[/dim]"
        )
    
    elif reason == "cooldown_active":
        return (
            f"🛡️ [red]Cooldown activo[/red]\n"
            f"   Espera: {retry} segundos\n"
            f"   [dim]Esto protege tu cuenta de accesos no autorizados.[/dim]"
        )
    
    elif reason == "abuse_detected":
        return (
            f"🛡️ [red]Actividad inusual detectada[/red]\n"
            f"   Por seguridad, espera {retry // 60} minutos.\n"
            f"   [dim]Si crees que es un error, contacta soporte.[/dim]"
        )
    
    else:
        return f"⚠️ [yellow]Acceso denegado: {reason}[/yellow]"

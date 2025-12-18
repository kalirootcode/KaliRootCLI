"""
Haptic Feedback Engine for Termux (Android).
Provides vibration patterns for different events using termux-vibrate.

Requirements:
- Termux:API app installed on Android
- termux-api package: pkg install termux-api
"""

import subprocess
import shutil
import time
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Check if we're on Termux with API available
def _is_termux_api_available() -> bool:
    """Check if termux-vibrate command is available."""
    return shutil.which("termux-vibrate") is not None


def vibrate(duration_ms: int = 100, force: bool = False) -> bool:
    """
    Trigger a single vibration.
    
    Args:
        duration_ms: Duration in milliseconds (default 100ms)
        force: Use force vibration if available (Android 8+)
    
    Returns:
        True if vibration was triggered, False otherwise
    """
    if not _is_termux_api_available():
        logger.debug("termux-vibrate not available, skipping haptic feedback")
        return False
    
    try:
        cmd = ["termux-vibrate", "-d", str(duration_ms)]
        if force:
            cmd.append("-f")
        
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False
        )
        return True
    except Exception as e:
        logger.debug(f"Haptic feedback failed: {e}")
        return False


def pattern_vibrate(pattern: List[int], pause_ms: int = 50) -> bool:
    """
    Execute a vibration pattern.
    
    Args:
        pattern: List of vibration durations in milliseconds
        pause_ms: Pause between vibrations
    
    Returns:
        True if pattern completed, False otherwise
    """
    if not _is_termux_api_available():
        return False
    
    for duration in pattern:
        vibrate(duration)
        time.sleep(pause_ms / 1000.0)
    
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# PRE-DEFINED PATTERNS (The "Wow" Factor)
# ═══════════════════════════════════════════════════════════════════════════════

def success_pulse() -> bool:
    """
    Success feedback - Double short pulse (heartbeat style).
    Used for: Login success, task completion, payment confirmed.
    """
    pattern = [50, 100]  # Two quick pulses
    return pattern_vibrate(pattern, pause_ms=80)


def error_pulse() -> bool:
    """
    Error feedback - Single long heavy vibration.
    Used for: Critical errors, authentication failures.
    """
    return vibrate(300, force=True)


def notification_pulse() -> bool:
    """
    Notification feedback - Triple light pulse.
    Used for: Scan complete, background task finished.
    """
    pattern = [30, 30, 30]  # Three gentle taps
    return pattern_vibrate(pattern, pause_ms=100)


def warning_pulse() -> bool:
    """
    Warning feedback - Two medium pulses.
    Used for: Low credits, session expiring.
    """
    pattern = [100, 100]
    return pattern_vibrate(pattern, pause_ms=150)


def payment_success() -> bool:
    """
    Payment success - Celebratory pattern.
    Used for: Payment confirmed, subscription activated.
    """
    pattern = [50, 50, 50, 150]  # Quick taps followed by a long confirmation
    return pattern_vibrate(pattern, pause_ms=60)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def is_haptics_available() -> bool:
    """Check if haptic feedback is available on this device."""
    return _is_termux_api_available()


def test_haptics() -> None:
    """Test all haptic patterns (for debugging)."""
    if not is_haptics_available():
        print("❌ Haptics not available (install termux-api)")
        return
    
    print("Testing haptic patterns...")
    
    print("  → Success pulse")
    success_pulse()
    time.sleep(0.5)
    
    print("  → Error pulse")
    error_pulse()
    time.sleep(0.5)
    
    print("  → Notification pulse")
    notification_pulse()
    time.sleep(0.5)
    
    print("  → Warning pulse")
    warning_pulse()
    time.sleep(0.5)
    
    print("  → Payment success")
    payment_success()
    
    print("✅ Haptic test complete!")


if __name__ == "__main__":
    test_haptics()

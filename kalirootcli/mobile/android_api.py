"""
Android Notifications and Share functionality for Termux.
Uses termux-notification and termux-share from Termux:API.

Requirements:
- Termux:API app installed on Android
- termux-api package: pkg install termux-api
"""

import subprocess
import shutil
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


def _is_termux_api_available() -> bool:
    """Check if termux-notification command is available."""
    return shutil.which("termux-notification") is not None


def _is_share_available() -> bool:
    """Check if termux-share command is available."""
    return shutil.which("termux-share") is not None


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def send_notification(
    title: str,
    content: str,
    notification_id: str = "krcli",
    priority: str = "high",
    vibrate: bool = True,
    led_color: str = "0064ff",  # KR-CLI blue
    sound: bool = True
) -> bool:
    """
    Send an Android push notification.
    
    Args:
        title: Notification title
        content: Notification body text
        notification_id: Unique ID for the notification (for updates/dismissal)
        priority: "min", "low", "default", "high", "max"
        vibrate: Enable vibration pattern
        led_color: LED color in hex (without #)
        sound: Play notification sound
    
    Returns:
        True if notification was sent, False otherwise
    """
    if not _is_termux_api_available():
        logger.debug("termux-notification not available")
        return False
    
    try:
        cmd = [
            "termux-notification",
            "--id", notification_id,
            "--title", title,
            "--content", content,
            "--priority", priority,
            "--led-color", led_color
        ]
        
        if vibrate:
            cmd.extend(["--vibrate", "100,100,100"])
        
        if not sound:
            cmd.append("--sound")  # termux-notification --sound disables sound
        
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False
        )
        return True
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        return False


def remove_notification(notification_id: str = "krcli") -> bool:
    """Remove a notification by ID."""
    if not _is_termux_api_available():
        return False
    
    try:
        subprocess.run(
            ["termux-notification-remove", notification_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False
        )
        return True
    except Exception:
        return False


# Pre-defined notification types
def notify_scan_complete(target: str = "") -> bool:
    """Notify when a scan or long task completes."""
    title = "🔍 Escaneo Completado"
    content = f"El análisis de {target} ha terminado." if target else "El análisis ha terminado."
    return send_notification(title, content, "krcli_scan")


def notify_payment_received() -> bool:
    """Notify when a payment is confirmed."""
    return send_notification(
        "💎 Pago Confirmado",
        "¡Tu compra ha sido procesada exitosamente!",
        "krcli_payment",
        priority="max",
        led_color="00ff00"  # Green
    )


def notify_low_credits(remaining: int) -> bool:
    """Notify when credits are running low."""
    return send_notification(
        "⚠️ Créditos Bajos",
        f"Te quedan {remaining} créditos. ¡Recarga para seguir operando!",
        "krcli_credits",
        priority="high",
        led_color="ffff00"  # Yellow
    )


def notify_error(message: str) -> bool:
    """Notify on critical error."""
    return send_notification(
        "❌ Error Crítico",
        message,
        "krcli_error",
        priority="max",
        led_color="ff0000"  # Red
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SHARE FUNCTIONALITY
# ═══════════════════════════════════════════════════════════════════════════════

def share_text(text: str, title: str = "Compartir desde KR-CLI") -> bool:
    """
    Share text via Android share sheet.
    
    Args:
        text: Text content to share
        title: Title for the share dialog
    
    Returns:
        True if share dialog was opened, False otherwise
    """
    if not _is_share_available():
        logger.debug("termux-share not available")
        return False
    
    try:
        subprocess.run(
            ["termux-share", "-a", "send", "-d", text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False
        )
        return True
    except Exception as e:
        logger.error(f"Share failed: {e}")
        return False


def share_file(file_path: str) -> bool:
    """
    Share a file via Android share sheet.
    
    Args:
        file_path: Path to the file to share
    
    Returns:
        True if share dialog was opened, False otherwise
    """
    if not _is_share_available():
        return False
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        subprocess.run(
            ["termux-share", file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False
        )
        return True
    except Exception as e:
        logger.error(f"Share file failed: {e}")
        return False


def share_report(report_content: str, filename: str = "kr_report.txt") -> bool:
    """
    Share a report by creating a temp file and sharing it.
    
    Args:
        report_content: The report text content
        filename: Name for the shared file
    
    Returns:
        True if share was successful
    """
    try:
        # Create temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return share_file(file_path)
    except Exception as e:
        logger.error(f"Share report failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# CLIPBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to Android clipboard using termux-clipboard-set.
    
    Args:
        text: Text to copy
    
    Returns:
        True if copied, False otherwise
    """
    if not shutil.which("termux-clipboard-set"):
        return False
    
    try:
        process = subprocess.Popen(
            ["termux-clipboard-set"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        process.communicate(input=text.encode("utf-8"), timeout=5)
        return process.returncode == 0
    except Exception:
        return False


def get_from_clipboard() -> Optional[str]:
    """
    Get text from Android clipboard using termux-clipboard-get.
    
    Returns:
        Clipboard content or None if unavailable
    """
    if not shutil.which("termux-clipboard-get"):
        return None
    
    try:
        result = subprocess.run(
            ["termux-clipboard-get"],
            capture_output=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8")
    except Exception:
        pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════════════════════

def is_android_api_available() -> bool:
    """Check if Android API features are available."""
    return _is_termux_api_available() or _is_share_available()

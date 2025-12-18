"""
Mobile-specific features for KaliRoot CLI.
Includes haptic feedback, notifications, and Android integrations.
"""

from .haptics import (
    vibrate,
    success_pulse,
    error_pulse,
    notification_pulse,
    warning_pulse,
    payment_success,
    is_haptics_available
)

from .android_api import (
    send_notification,
    notify_scan_complete,
    notify_payment_received,
    notify_low_credits,
    share_text,
    share_file,
    share_report,
    copy_to_clipboard,
    get_from_clipboard,
    is_android_api_available
)

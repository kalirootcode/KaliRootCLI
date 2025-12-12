"""
Database Manager for KaliRoot CLI
Handles all Supabase operations for user management, credits, and subscriptions.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from supabase import create_client, Client

from .config import (
    SUPABASE_URL, 
    SUPABASE_ANON_KEY, 
    SUPABASE_SERVICE_KEY,
    DEFAULT_CREDITS_ON_REGISTER
)

logger = logging.getLogger(__name__)

# Initialize Supabase client
_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client."""
    global _supabase
    
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError("Supabase credentials not configured")
        
        # Prefer service key for server operations
        key = SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY
        _supabase = create_client(SUPABASE_URL, key)
        
        if SUPABASE_SERVICE_KEY:
            logger.info("Using SUPABASE_SERVICE_KEY for DB operations")
        else:
            logger.info("Using SUPABASE_ANON_KEY for DB operations")
    
    return _supabase


def test_connection() -> bool:
    """Test database connection."""
    try:
        supabase = get_supabase()
        # Try to select from cli_users
        res = supabase.table("cli_users").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def register_user(username: str, password_hash: str) -> Optional[dict]:
    """
    Register a new CLI user.
    
    Returns:
        dict with {id, username} if successful, None if failed
    """
    try:
        supabase = get_supabase()
        
        # Use RPC function for registration
        result = supabase.rpc(
            "register_cli_user",
            {
                "p_username": username,
                "p_password_hash": password_hash,
                "p_initial_credits": DEFAULT_CREDITS_ON_REGISTER
            }
        ).execute()
        
        if result.data and len(result.data) > 0:
            user = result.data[0]
            logger.info(f"Registered new user: {username}")
            return {"id": user["id"], "username": user["username"]}
        
        return None
        
    except Exception as e:
        error_msg = str(e)
        if "unique" in error_msg.lower() or "already exists" in error_msg.lower():
            logger.warning(f"Username already exists: {username}")
        else:
            logger.error(f"Error registering user: {e}")
        return None


def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user by username.
    
    Returns:
        dict with user data or None if not found
    """
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "get_cli_user_by_username",
            {"p_username": username}
        ).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None


def get_user_credits(user_id: str) -> int:
    """Get user's credit balance."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("cli_users") \
            .select("credit_balance") \
            .eq("id", user_id) \
            .single() \
            .execute()
        
        if result.data:
            return result.data.get("credit_balance", 0)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error getting user credits: {e}")
        return 0


def deduct_credit(user_id: str) -> bool:
    """
    Deduct one credit from user.
    Premium users don't consume credits.
    
    Returns:
        True if successful or user is premium, False if no credits
    """
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "deduct_cli_credit",
            {"p_user_id": user_id}
        ).execute()
        
        # Handle different response formats
        if isinstance(result.data, bool):
            return result.data
        elif isinstance(result.data, list) and len(result.data) > 0:
            return bool(result.data[0])
        
        return False
        
    except Exception as e:
        logger.error(f"Error deducting credit: {e}")
        return False


def add_credits(user_id: str, amount: int) -> bool:
    """Add credits to user account."""
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "add_cli_credits",
            {"p_user_id": user_id, "p_amount": amount}
        ).execute()
        
        logger.info(f"Added {amount} credits to user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        return False


def is_user_subscribed(user_id: str) -> bool:
    """Check if user has active premium subscription."""
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "check_cli_subscription",
            {"p_user_id": user_id}
        ).execute()
        
        if isinstance(result.data, bool):
            return result.data
        elif isinstance(result.data, list) and len(result.data) > 0:
            return bool(result.data[0])
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False


def activate_subscription(user_id: str, invoice_id: str) -> bool:
    """Activate premium subscription for user."""
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "activate_cli_subscription",
            {"p_user_id": user_id, "p_invoice_id": invoice_id}
        ).execute()
        
        if isinstance(result.data, bool) and result.data:
            logger.info(f"Activated subscription for user {user_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error activating subscription: {e}")
        return False


def set_subscription_pending(user_id: str, invoice_id: str) -> bool:
    """Set subscription status to pending."""
    try:
        supabase = get_supabase()
        
        result = supabase.rpc(
            "set_cli_subscription_pending",
            {"p_user_id": user_id, "p_invoice_id": invoice_id}
        ).execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting pending subscription: {e}")
        return False


def get_user_profile(user_id: str) -> Optional[dict]:
    """Get full user profile."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("cli_users") \
            .select("*") \
            .eq("id", user_id) \
            .single() \
            .execute()
        
        return result.data
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return None


def save_chat_interaction(user_id: str, user_msg: str, ai_msg: str) -> bool:
    """Save chat interaction to history."""
    try:
        supabase = get_supabase()
        
        # Save user message
        supabase.table("cli_chat_history").insert({
            "user_id": user_id,
            "role": "user",
            "content": user_msg
        }).execute()
        
        # Save AI response
        supabase.table("cli_chat_history").insert({
            "user_id": user_id,
            "role": "assistant",
            "content": ai_msg
        }).execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving chat interaction: {e}")
        return False


def get_chat_history(user_id: str, limit: int = 6) -> str:
    """Get recent chat history formatted as string."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("cli_chat_history") \
            .select("role, content") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        if not result.data:
            return ""
        
        # Reverse to get chronological order
        messages = result.data[::-1]
        
        history = ""
        for msg in messages:
            role = "Usuario" if msg["role"] == "user" else "KaliRoot (AI)"
            history += f"{role}: {msg['content']}\n"
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return ""


def get_subscription_info(user_id: str) -> Optional[dict]:
    """Get subscription details."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("cli_users") \
            .select("subscription_status, subscription_expiry_date") \
            .eq("id", user_id) \
            .single() \
            .execute()
        
        if result.data:
            status = result.data.get("subscription_status", "free")
            expiry = result.data.get("subscription_expiry_date")
            
            # Parse expiry date
            if expiry:
                try:
                    expiry_date = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                    days_left = (expiry_date - datetime.now(expiry_date.tzinfo)).days
                except:
                    days_left = 0
            else:
                days_left = 0
            
            return {
                "status": status,
                "expiry_date": expiry,
                "days_left": max(0, days_left),
                "is_active": status == "premium" and days_left > 0
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}")
        return None

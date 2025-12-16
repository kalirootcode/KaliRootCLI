"""
Configuration module for KaliRoot CLI
Loads environment variables and provides configuration constants
"""

import os
import pathlib
from dotenv import load_dotenv

# Logic for global config path (consistent with api_client)
if os.path.exists("/data/data/com.termux"):
    GLOBAL_CONFIG_DIR = pathlib.Path.home() / ".krcli"
else:
    GLOBAL_CONFIG_DIR = pathlib.Path.home() / ".config" / "krcli"

# 1. Load from current dir (Priority)
load_dotenv()

# 2. Load from global config (Fallback)
global_env = GLOBAL_CONFIG_DIR / ".env"
if global_env.exists():
    load_dotenv(global_env)

# ===== SUPABASE =====
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip() or None
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip() or None
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "").strip() or None

# ===== AI (GROQ) =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() or None
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# ===== PAYMENTS =====
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "").strip() or None
IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY", "").strip() or None

# ===== APP SETTINGS =====
DEFAULT_CREDITS_ON_REGISTER = int(os.getenv("DEFAULT_CREDITS_ON_REGISTER", "500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ===== PRICING =====
SUBSCRIPTION_PRICE_USD = 20.0
SUBSCRIPTION_BONUS_CREDITS = 1200

CREDIT_PACKAGES = [
    {"name": "Starter", "credits": 500, "price": 10.0},
    {"name": "Hacker Pro", "credits": 1200, "price": 20.0},
    {"name": "Elite", "credits": 2500, "price": 35.0},
]

# ===== FALLBACK MESSAGES =====
FALLBACK_AI_TEXT = "Lo siento, no puedo procesar tu pregunta en este momento. Inténtalo más tarde."


def validate_config(require_all: bool = True) -> list:
    """
    Validate configuration.
    Returns list of missing required variables.
    """
    missing = []
    
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "GROQ_API_KEY"]
    
    if require_all:
        required_vars.extend(["NOWPAYMENTS_API_KEY", "IPN_SECRET_KEY"])
    
    for var in required_vars:
        if globals().get(var) is None:
            missing.append(var)
    
    return missing


def get_config_status() -> dict:
    """Get configuration status for display."""
    return {
        "supabase": bool(SUPABASE_URL and SUPABASE_ANON_KEY),
        "groq": bool(GROQ_API_KEY),
        "payments": bool(NOWPAYMENTS_API_KEY),
        "service_key": bool(SUPABASE_SERVICE_KEY),
    }

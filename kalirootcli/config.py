"""
Configuration module for KaliRoot CLI — DOMINION Edition
Loads environment variables and provides configuration constants.
Economy: KR Credits system. AI: Google Gemini.
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

# ===== AI (GEMINI — Google Generative AI) =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or None
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ===== PAYMENTS =====
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "").strip() or None
IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY", "").strip() or None

# ===== APP SETTINGS =====
DEFAULT_CREDITS_ON_REGISTER = int(os.getenv("DEFAULT_CREDITS_ON_REGISTER", "100"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ===== KR CREDITS ECONOMY =====
# Cost per action in KR credits
KR_COST_CHAT = 1       # Per AI consultation / chat message
KR_COST_AGENT = 5      # Per agent action (file creation, project scaffolding)
KR_COST_REPORT = 10    # Per executive report generation

# ===== KR RECHARGE PACKAGES =====
KR_PACKAGES = [
    {"name": "KR-100  · Starter",    "credits": 100,  "price": 5.0},
    {"name": "KR-500  · Operative",  "credits": 500,  "price": 20.0},
    {"name": "KR-1000 · DOMINION",   "credits": 1000, "price": 35.0},
]

# Legacy alias — kept for any code that still references CREDIT_PACKAGES
CREDIT_PACKAGES = KR_PACKAGES

# ===== STORE LINKS =====
DOMINION_STORE_URL = "https://kalirootcode.github.io/KaliRootCLI/links.html"

# ===== FALLBACK MESSAGES =====
FALLBACK_AI_TEXT = "Lo siento, no puedo procesar tu pregunta en este momento. Inténtalo más tarde."


def validate_config(require_all: bool = True) -> list:
    """
    Validate configuration.
    Returns list of missing required variables.
    """
    missing = []

    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "GEMINI_API_KEY"]

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
        "gemini": bool(GEMINI_API_KEY),
        "payments": bool(NOWPAYMENTS_API_KEY),
        "service_key": bool(SUPABASE_SERVICE_KEY),
    }

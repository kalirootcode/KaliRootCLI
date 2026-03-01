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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


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

# ===== DOMINION TIER PACKAGES =====
KR_PACKAGES = [
    {
        "id": "starter",
        "name": "⚡ Dominion Starter",
        "credits": 250,
        "price": 10.0,
        "tier": "starter",
        "emoji": "⚡",
        "tagline": "Tu primer paso hacia el poder ofensivo",
        "features": [
            "250 KR para consultas de IA ilimitadas",
            "Acceso Núcleo Dominion Flash",
            "Terminal inteligente con autocompletado",
            "Historial de sesiones encriptado",
            "Soporte de red TOR integrado",
        ],
    },
    {
        "id": "hacker",
        "name": "🚀 Hacker Promo",
        "credits": 1500,
        "price": 25.0,
        "tier": "hacker",
        "emoji": "🚀",
        "tagline": "El arsenal que todo pentester necesita — 6X más KR por tu dinero",
        "features": [
            "1,500 KR — 🔥 DOBLE KR vs Starter",
            "Agente de Proyectos autónomo (crea estructuras con 1 comando)",
            "Scanner de Puertos + CVE Lookup automático",
            "Modelo IA con 8K tokens de contexto",
            "Análisis profundo de vulnerabilidades",
            "Generación de reportes ejecutivos",
        ],
    },
    {
        "id": "god_mode",
        "name": "💀 Dominion God Mode",
        "credits": 4000,
        "price": 50.0,
        "tier": "god_mode",
        "emoji": "💀",
        "tagline": "Poder absoluto. Sin restricciones. Sin piedad.",
        "features": [
            "4,000 KR — ☠️ 16X más que Starter",
            "Arsenal Prohibido: exploits + payloads avanzados",
            "Modelo IA de alta precisión (16K tokens / temp 0.2)",
            "Modo Agente Autónomo ilimitado",
            "Acceso a herramientas clasificadas",
            "Banner visual God Mode en tu terminal",
            "Soporte prioritario del equipo Dominion",
        ],
    },
]

# Legacy alias
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

"""
subscription.py — Legacy Compatibility Shim
============================================
This file has been superseded by economy.py in the DOMINION refactoring.
All classes and functions are re-exported from economy.py for backward compatibility.
Do NOT add new logic here; use economy.py directly.
"""

# Re-export everything from the new economy module
from .economy import (  # noqa: F401
    EconomyManager,
    EconomyManager as SubscriptionManager,  # legacy alias
    show_zero_balance_panel,
    show_kr_spend_panel,
    get_kr_packages_display,
    get_kr_packages_display as get_credits_packages_display,  # legacy alias
)
from .config import KR_PACKAGES as CREDIT_PACKAGES  # noqa: F401


def get_plan_comparison() -> str:
    """Legacy function — returns DOMINION tier description."""
    return """
[bold cyan]⚡ TIER: DOMINION[/bold cyan]
 • Acceso completo a todas las funciones de IA
 • Modo Agente de Automatización habilitado
 • Generación de Scripts, Exploits y Payloads
 • Reportes ejecutivos en PDF
 • Economía basada en créditos KR

[dim]Recarga KR en: kalirootcode.github.io/KaliRootCLI/links.html[/dim]
"""

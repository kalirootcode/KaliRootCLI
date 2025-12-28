"""
Subscription Handler for KaliRoot CLI
Manages free vs premium tier gating and subscription status.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .database_manager import (
    is_user_subscribed,
    get_user_credits,
    get_subscription_info,
    set_subscription_pending
)
from .api_client import api_client
from .config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Manages subscription and credit operations."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.is_premium: bool = False
        self.credits: int = 0
        self.expiry_date = None
        self.refresh()
    
    def refresh(self) -> None:
        """Syncs local state with backend source of truth."""
        try:
            status = api_client.get_status()
            if status["success"]:
                data = status["data"]
                self.credits = data.get("credits", 0)
                self.is_premium = data.get("is_premium", False)
                self.expiry_date = None # simplified for api response
                
                # Check if we have detailed expiry
                # This depends on API response structure, but basic isPremium is enough for CLI
        except Exception as e:
            logger.error(f"Error refreshing subscription: {e}")

    def get_subscription_details(self) -> Dict[str, Any]:
        """Get formatted subscription details for UI."""
        return {
            "credits": self.credits,
            "is_premium": self.is_premium,
            "days_left": 30 if self.is_premium else 0, # Placeholder or need API update
            "expiry_date": "Active" if self.is_premium else "N/A"
        }

    def start_subscription_flow(self) -> None:
        """Initiate the Premium subscription upgrade flow."""
        try:
            print_info("Connecting to Payment Gateway...")
            
            with show_loading("Generating Secure Invoice..."):
                invoice = api_client.create_subscription_invoice()
            
            if not invoice or not invoice.get("success"):
                error = invoice.get("error", "Unknown error") if invoice else "Response Error"
                print_error(f"Failed to generate invoice: {error}")
                return
            
            invoice_url = invoice["invoice_url"]
            print_success(f"Invoice Generated: {invoice.get('invoice_id', 'N/A')}")
            
            from .distro_detector import detector
            if detector.open_url(invoice_url):
                print_success("Browser opened. Please complete payment.")
            else:
                print_info(f"Please open this URL to pay: {invoice_url}")
                
        except Exception as e:
            logger.error(f"Subscription flow error: {e}")
            print_error("Transaction initialization failed.")

    def start_credits_flow(self, package_index: int) -> None:
        """Initiate credits purchase flow."""
        if not (0 <= package_index < len(CREDIT_PACKAGES)):
            print_error("Invalid package selection.")
            return
            
        pkg = CREDIT_PACKAGES[package_index]
        
        try:
            print_info(f"Initiating purchase: {pkg['credits']} Credits for ${pkg['price']}")
            
            with show_loading("Generating Invoice..."):
                invoice = api_client.create_credits_invoice(
                    pkg["price"],
                    pkg["credits"]
                )
            
            if not invoice or not invoice.get("success"):
                error = invoice.get("error", "Unknown error") if invoice else "Response Error"
                print_error(f"Failed to generate invoice: {error}")
                return
            
            invoice_url = invoice.get("invoice_url")
            if not invoice_url:
                print_error("No invoice URL returned.")
                return

            from .distro_detector import detector
            if detector.open_url(invoice_url):
                print_success("Browser opened. Listening for completion...")
            else:
                print_info(f"Pay here: {invoice_url}")
                
        except Exception as e:
            logger.error(f"Credits flow error: {e}")
            print_error("Purchase failed.")

    def get_status_display(self) -> str:
        """Get textual status for top bar."""
        if self.is_premium:
            return "[bold green]OPERATIONAL (PREMIUM)[/bold green]"
        return f"[yellow]CONSULTATION (FREE) | {self.credits} Credits[/yellow]"


def get_plan_comparison() -> str:
    """Return the comparison text for the UI."""
    return """
[bold cyan]─── PAQUETE STARTER (FREE / BASIC) ───[/bold cyan]
 • 500 créditos iniciales
 • Modelo AI Standard
 • Consultas básicas
 • Validéz de pack: 30 días
 • [dim]$10 USD (Si se recarga)[/dim]

[bold green]👑 PAQUETE PREMIUM (SUBSCRIPCIÓN) ───[/bold green]
 • [bold]1200 créditos mensuales[/bold]
 • [bold]Modelo AI 70B (respuestas profesionales)[/bold]
 • [bold]Port Scanner, CVE Lookup, Script Generator[/bold]
 • [bold]Modo Agente para crear proyectos[/bold]
 • [bold]Historial ilimitado de chats[/bold]
 
 PRICE: $20 USD/mes (USDT)
"""


def get_credits_packages_display() -> str:
    """Get formatted credits packages table."""
    from rich.table import Table
    from rich import box
    
    table = Table(
        title="⚡ Paquetes de Créditos",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("#", style="white", justify="center", width=3)
    table.add_column("Paquete", style="white")
    table.add_column("Créditos", style="green", justify="center")
    table.add_column("Precio", style="yellow", justify="center")
    table.add_column("Extra", style="cyan", justify="center")
    
    for i, pkg in enumerate(CREDIT_PACKAGES, 1):
        extra = ""
        if pkg["credits"] == 900:
            extra = "+12%"
        elif pkg["credits"] == 1500:
            extra = "🔥 Best Deal"
        
        table.add_row(
            str(i),
            pkg["name"],
            str(pkg["credits"]),
            f"${pkg['price']:.2f}",
            extra
        )
    
    return table

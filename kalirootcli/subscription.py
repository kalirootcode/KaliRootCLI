"""
Subscription Handler for KaliRoot CLI
Manages free vs premium tier gating and subscription status.
"""

import logging
from typing import Optional
from datetime import datetime

from .database_manager import (
    is_user_subscribed,
    get_user_credits,
    get_subscription_info,
    set_subscription_pending
)
from .payments import payment_manager, create_subscription_invoice, create_credits_invoice
from .config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Manages subscription and credit operations."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._is_premium: Optional[bool] = None
        self._credits: Optional[int] = None
    
    def refresh(self) -> None:
        """Refresh cached subscription status."""
        self._is_premium = None
        self._credits = None
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        if self._is_premium is None:
            self._is_premium = is_user_subscribed(self.user_id)
        return self._is_premium
    
    @property
    def credits(self) -> int:
        """Get user's credit balance."""
        if self._credits is None:
            self._credits = get_user_credits(self.user_id)
        return self._credits
    
    def can_use_ai(self) -> bool:
        """Check if user can use AI (has credits or is premium)."""
        return self.is_premium or self.credits > 0
    
    def get_status_display(self) -> str:
        """Get formatted status display."""
        if self.is_premium:
            info = get_subscription_info(self.user_id)
            days_left = info.get("days_left", 0) if info else 0
            return f"💎 Premium ({days_left} días restantes)"
        else:
            return f"🆓 Free ({self.credits} créditos)"
    
    def get_subscription_details(self) -> dict:
        """Get detailed subscription info."""
        info = get_subscription_info(self.user_id)
        
        if info is None:
            return {
                "status": "free",
                "is_premium": False,
                "credits": self.credits,
                "days_left": 0,
                "expiry_date": None
            }
        
        return {
            "status": info.get("status", "free"),
            "is_premium": info.get("is_active", False),
            "credits": self.credits,
            "days_left": info.get("days_left", 0),
            "expiry_date": info.get("expiry_date")
        }
    
    def start_subscription_flow(self) -> Optional[str]:
        """
        Start subscription purchase flow.
        
        Returns:
            Payment URL if successful, None on failure
        """
        from .ui.display import print_info, print_error, print_success, console
        
        print_info("Generando enlace de pago...")
        
        invoice = create_subscription_invoice(self.user_id)
        
        if not invoice or not invoice.get("invoice_url"):
            print_error("Error al generar el enlace de pago")
            return None
        
        # Set subscription as pending
        set_subscription_pending(self.user_id, invoice.get("invoice_id", ""))
        
        url = invoice["invoice_url"]
        
        # Try to open browser
        if payment_manager.open_payment_url(url):
            print_success("✅ Navegador abierto con el enlace de pago")
        else:
            console.print(f"\n[yellow]No se pudo abrir el navegador automáticamente.[/yellow]")
            console.print(f"[cyan]Copia y abre este enlace:[/cyan]")
            console.print(f"[bold blue]{url}[/bold blue]\n")
        
        return url
    
    def start_credits_flow(self, package_index: int) -> Optional[str]:
        """
        Start credits purchase flow.
        
        Args:
            package_index: Index of package in CREDIT_PACKAGES
        
        Returns:
            Payment URL if successful, None on failure
        """
        from .ui.display import print_info, print_error, print_success, console
        
        if package_index < 0 or package_index >= len(CREDIT_PACKAGES):
            print_error("Paquete no válido")
            return None
        
        package = CREDIT_PACKAGES[package_index]
        
        print_info(f"Generando enlace para {package['credits']} créditos...")
        
        invoice = create_credits_invoice(
            self.user_id,
            package["credits"],
            package["price"]
        )
        
        if not invoice or not invoice.get("invoice_url"):
            print_error("Error al generar el enlace de pago")
            return None
        
        url = invoice["invoice_url"]
        
        # Try to open browser
        if payment_manager.open_payment_url(url):
            print_success("✅ Navegador abierto con el enlace de pago")
        else:
            console.print(f"\n[yellow]No se pudo abrir el navegador automáticamente.[/yellow]")
            console.print(f"[cyan]Copia y abre este enlace:[/cyan]")
            console.print(f"[bold blue]{url}[/bold blue]\n")
        
        return url


def get_plan_comparison() -> str:
    """Get formatted plan comparison table."""
    from rich.table import Table
    from rich import box
    
    table = Table(
        title="💎 Planes Disponibles",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Característica", style="white")
    table.add_column("Free", style="yellow", justify="center")
    table.add_column("Premium", style="green", justify="center")
    
    table.add_row("Consultas IA", "5/día", "∞ Ilimitadas")
    table.add_row("Historial de Chat", "Limitado", "Completo")
    table.add_row("Modo Sin Censura", "❌", "✅")
    table.add_row("Soporte", "Comunidad", "Prioritario")
    table.add_row("Créditos Bonus", "-", "+250/mes")
    table.add_row("", "", "")
    table.add_row("Precio", "$0", f"${SUBSCRIPTION_PRICE_USD}/mes")
    
    return table


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

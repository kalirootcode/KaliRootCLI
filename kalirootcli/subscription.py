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
from .payments import PaymentManager, payment_manager, create_subscription_invoice, create_credits_invoice
from .config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Manages subscription and credit operations."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.is_premium: bool = False
        self.credits: int = 0
        self.expiry_date = None
        self.payment_manager = PaymentManager()
        self.refresh()
    
    def refresh(self) -> None:
        """Syncs local state with backend source of truth."""
        try:
            profile = get_user_profile(self.user_id)
            if not profile:
                return
            
            self.credits = profile.get("credit_balance", 0)
            
            sub_status = check_subscription_status(self.user_id)
            self.is_premium = sub_status["is_active"]
            
            if sub_status["expiry_date"]:
                # Parse ISO format if string
                if isinstance(sub_status["expiry_date"], str):
                    try:
                        self.expiry_date = datetime.fromisoformat(sub_status["expiry_date"].replace('Z', '+00:00'))
                    except ValueError:
                        self.expiry_date = None
                else:
                    self.expiry_date = sub_status["expiry_date"]
                    
        except Exception as e:
            logger.error(f"Error refreshing subscription: {e}")

    def get_subscription_details(self) -> Dict[str, Any]:
        """Get formatted subscription details for UI."""
        days_left = 0
        if self.expiry_date:
            delta = self.expiry_date - datetime.now(self.expiry_date.tzinfo)
            days_left = max(0, delta.days)
            
        return {
            "credits": self.credits,
            "is_premium": self.is_premium,
            "days_left": days_left,
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d") if self.expiry_date else "N/A"
        }

    def start_subscription_flow(self) -> None:
        """Initiate the Premium subscription upgrade flow."""
        try:
            print_info("Connecting to Payment Gateway...")
            
            with show_loading("Generating Secure Invoice..."):
                invoice = self.payment_manager.create_subscription_invoice(self.user_id)
            
            if not invoice or "invoice_url" not in invoice:
                print_error("Failed to generate invoice. Try again later.")
                return
            
            invoice_url = invoice["invoice_url"]
            print_success(f"Invoice Generated: {invoice['id']}")
            
            if self.payment_manager.open_payment_url(invoice_url):
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
                invoice = self.payment_manager.create_credits_invoice(
                    self.user_id, 
                    pkg["credits"], 
                    pkg["price"]
                )
            
            if not invoice or "invoice_url" not in invoice:
                print_error("Failed to generate invoice.")
                return
            
            if self.payment_manager.open_payment_url(invoice["invoice_url"]):
                print_success("Browser opened. Listening for completion...")
            else:
                print_info(f"Pay here: {invoice['invoice_url']}")
                
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
[bold cyan]─── CONSULTATION (FREE) ───[/bold cyan]
 • Basic AI Q&A
 • Educational Explanations
 • Manual Execution
 • Rate Limited
 • 5 Daily Credits

[bold green]─── OPERATIONAL (PREMIUM) ───[/bold green]
 • [bold]Full Script Generation[/bold]
 • [bold]Vulnerability Analysis[/bold]
 • [bold]Automated Workflows[/bold]
 • [bold]Priority Processing[/bold]
 • [bold]Unlimited Queries[/bold]
 • [bold]+250 Bonus Credits/mo[/bold]
 
 PRICE: $10.00 / Month
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

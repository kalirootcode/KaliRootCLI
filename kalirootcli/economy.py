"""
Economy Manager for KaliRoot CLI — DOMINION Edition
Manages KR credit balance, recharge flows, and spend display.

Replaces the legacy subscription.py — no Free/Premium distinction.
All users are in the DOMINION tier; access is governed by KR balance.
"""

import logging
from typing import Optional, Dict, Any

from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.console import Console

from .api_client import api_client
from .config import KR_PACKAGES, DOMINION_STORE_URL

logger = logging.getLogger(__name__)
console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# ZERO-BALANCE REDIRECT
# ═══════════════════════════════════════════════════════════════════════════════

def show_zero_balance_panel() -> None:
    """Display an elegant redirect panel when KR balance is 0."""
    console.print(Panel(
        f"""[bold red]⛔  SALDO KR INSUFICIENTE[/bold red]

[white]Necesitas créditos KR para usar esta función.[/white]

[bold cyan]➜  Recarga tu billetera:[/bold cyan]
[link={DOMINION_STORE_URL}][underline cyan]{DOMINION_STORE_URL}[/underline cyan][/link]

[dim]KR-100 · KR-500 · KR-1000 — Elige el paquete que necesitas.[/dim]""",
        title="[bold yellow]⚡ DOMINION · KR WALLET[/bold yellow]",
        border_style="red",
        padding=(1, 4),
    ))


def show_kr_spend_panel(cost: int, action: str = "Operación") -> None:
    """Show an elegant spend notification panel before an AI action."""
    console.print(Panel(
        f"[bold cyan]⚡ {action}[/bold cyan]  [dim]—[/dim]  [bold yellow]-{cost} KR[/bold yellow]",
        style="dim",
        border_style="rgb(0,200,180)",
        padding=(0, 2),
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# ECONOMY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class EconomyManager:
    """
    KR Credit Economy Manager for DOMINION CLI.
    Syncs balance with backend and exposes recharge flows.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.kr_balance: int = 0
        self.refresh()

    def refresh(self) -> None:
        """Sync local KR balance with backend source of truth."""
        try:
            balance = api_client.get_kr_balance()
            self.kr_balance = balance if balance is not None else 0
        except Exception as e:
            logger.error(f"Error refreshing KR balance: {e}")

    def has_balance(self, cost: int = 1) -> bool:
        """Check if user has enough KR for an action."""
        return self.kr_balance >= cost

    def get_balance_display(self) -> str:
        """Return a Rich-formatted balance string for inline display."""
        return f"[bold cyan]⚡ Billetera KR: {self.kr_balance} KR[/bold cyan]"

    def get_details(self) -> Dict[str, Any]:
        """Return a dict of economy details for UI rendering."""
        return {
            "kr_balance": self.kr_balance,
        }

    # ─── Recharge Flow ───────────────────────────────────────────────────────

    def start_kr_recharge_flow(self, package_index: int) -> None:
        """Initiate a KR package purchase via payment gateway."""
        if not (0 <= package_index < len(KR_PACKAGES)):
            from .ui.display import print_error
            print_error("Selección de paquete inválida.")
            return

        pkg = KR_PACKAGES[package_index]

        from .ui.display import print_info, print_error, print_success, show_loading

        print_info(f"Iniciando recarga: {pkg['name']} — {pkg['credits']} KR por ${pkg['price']:.2f}")

        try:
            with show_loading("Generando factura segura..."):
                invoice = api_client.create_credits_invoice(
                    pkg["id"]
                )

            if not invoice or not invoice.get("success"):
                error = invoice.get("error", "Error desconocido") if invoice else "Sin respuesta"
                print_error(f"No se pudo generar la factura: {error}")
                return

            invoice_url = invoice.get("invoice_url")
            if not invoice_url:
                print_error("URL de factura no disponible.")
                return

            print_success(f"Factura generada: {invoice.get('invoice_id', 'N/A')}")

            from .distro_detector import detector
            if detector.open_url(invoice_url):
                print_success("Navegador abierto. Completa el pago para acreditar tu saldo.")
            else:
                print_info(f"Paga aquí: {invoice_url}")

        except Exception as e:
            logger.error(f"Recharge flow error: {e}")
            from .ui.display import print_error
            print_error("Error iniciando la recarga.")


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_kr_packages_display():
    """Get a formatted Rich table of KR recharge packages."""
    table = Table(
        title="[bold cyan]⚡ Paquetes de Recarga KR — DOMINION[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="rgb(0,200,180)",
    )

    table.add_column("#",       style="white",       justify="center", width=3)
    table.add_column("Paquete", style="bold white")
    table.add_column("KR",      style="bold cyan",   justify="center")
    table.add_column("Precio",  style="bold yellow",  justify="center")
    table.add_column("Valor",   style="green",        justify="center")

    badges = ["⚡ Starter", "🔥 Hacker Promo", "💀 GOD MODE"]

    for i, pkg in enumerate(KR_PACKAGES):
        table.add_row(
            str(i + 1),
            pkg["name"],
            str(pkg["credits"]),
            f"${pkg['price']:.2f}",
            badges[i] if i < len(badges) else "",
        )

    return table


# ─── Legacy shim — allows old imports to keep working during migration ────────
# Any module that still does `from .subscription import SubscriptionManager`
# will get EconomyManager transparently.
SubscriptionManager = EconomyManager

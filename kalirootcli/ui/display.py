"""
Display utilities for KaliRoot CLI
Uses Rich library for beautiful terminal output.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box


# Global console instance
console = Console()


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]❌ {message}[/red]")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✅ {message}[/green]")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")


def print_banner() -> None:
    """Print the application banner."""
    banner_text = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗  ██╗ █████╗ ██╗     ██╗██████╗  ██████╗  ██████╗████████╗   ║
║   ██║ ██╔╝██╔══██╗██║     ██║██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝   ║
║   █████╔╝ ███████║██║     ██║██████╔╝██║   ██║██║   ██║   ██║      ║
║   ██╔═██╗ ██╔══██║██║     ██║██╔══██╗██║   ██║██║   ██║   ██║      ║
║   ██║  ██╗██║  ██║███████╗██║██║  ██║╚██████╔╝╚██████╔╝   ██║      ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝      ║
║                                                           ║
║            💀 CLI Edition - Termux & Kali Linux 💀        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(banner_text, style="bold cyan")


def print_mini_banner() -> None:
    """Print a smaller banner for menus."""
    console.print("\n[bold cyan]═══ KALIROOT CLI ═══[/bold cyan]\n")


def print_divider(char: str = "─", width: int = 50) -> None:
    """Print a divider line."""
    console.print(f"[dim]{char * width}[/dim]")


def print_header(title: str) -> None:
    """Print a section header."""
    console.print(f"\n[bold cyan]═══ {title} ═══[/bold cyan]\n")


def print_menu_option(number: str, text: str, emoji: str = "") -> None:
    """Print a menu option."""
    emoji_str = f"{emoji} " if emoji else ""
    console.print(f"  [cyan]{number}.[/cyan] {emoji_str}{text}")


def print_panel(content: str, title: str = "", style: str = "cyan") -> None:
    """Print content in a panel."""
    console.print(Panel(
        content,
        title=f"[bold]{title}[/bold]" if title else None,
        border_style=style,
        box=box.ROUNDED
    ))


def print_ai_response(response: str) -> None:
    """Print AI response in a styled panel."""
    console.print("\n")
    console.print(Panel(
        response,
        title="[bold cyan]💀 KaliRoot AI[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print("\n")


def clear_screen() -> None:
    """Clear the terminal screen."""
    console.clear()


def get_input(prompt: str = ">>> ") -> str:
    """Get user input with styled prompt."""
    return console.input(f"[bold cyan]{prompt}[/bold cyan]").strip()


def confirm(message: str) -> bool:
    """Ask for confirmation."""
    response = console.input(f"[yellow]{message} (s/n): [/yellow]").strip().lower()
    return response in ['s', 'si', 'sí', 'y', 'yes']


def show_loading(message: str = "Cargando..."):
    """Show loading spinner."""
    return console.status(f"[cyan]{message}[/cyan]", spinner="dots")

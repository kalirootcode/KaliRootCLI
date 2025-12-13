"""
Display utilities for KaliRoot CLI
Professional terminal output using Rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.prompt import Prompt, Confirm

# Global console instance
console = Console()


def print_error(message: str) -> None:
    """Print professional error message."""
    console.print(f"[bold red]❌ ERROR:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✅ SUCCESS:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold yellow]⚠️  WARNING:[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold blue]ℹ️  INFO:[/bold blue] {message}")


def print_banner() -> None:
    """Print the professional application banner."""
    banner = """
    ██╗  ██╗ █████╗ ██╗     ██╗██████╗  ██████╗  ██████╗ ████████╗
    ██║  ██║██╔══██╗██║     ██║██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝
    █████╔╝███████║██║     ██║██████╔╝██║   ██║██║   ██║   ██║   
    ██╔═██╗██╔══██║██║     ██║██╔══██╗██║   ██║██║   ██║   ██║   
    ██║  ██╗██║  ██║███████╗██║██║  ██║╚██████╔╝╚██████╔╝   ██║   
    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   
             >>> ADVANCED SECURITY OPERATIONS CLI <<<
    """
    console.print(Panel(
        Text(banner, style="bold cyan", justify="center"),
        box=box.HEAVY,
        border_style="blue",
        title="[bold white]v1.0.0[/bold white]"
    ))


def print_divider(title: str = "") -> None:
    """Print a divider with optional title."""
    if title:
        console.rule(f"[bold cyan]{title}[/bold cyan]")
    else:
        console.rule(style="dim blue")


def print_header(title: str) -> None:
    """Print a main section header."""
    console.print(f"\n[bold white on blue] {title.upper()} [/bold white on blue]\n")


def print_menu_option(number: str, text: str, description: str = "") -> None:
    """Print a menu option with description."""
    console.print(f" [cyan bold]{number}[/cyan bold] › [white bold]{text}[/white bold]")
    if description:
        console.print(f"    [dim]{description}[/dim]")


def print_panel(content: str, title: str = "", style: str = "cyan") -> None:
    """Print content in a panel."""
    console.print(Panel(
        content,
        title=f"[bold]{title}[/bold]" if title else None,
        border_style=style,
        box=box.ROUNDED,
        padding=(1, 2)
    ))


def print_ai_response(response: str, mode: str = "CONSULTATION") -> None:
    """Print AI response in a styled panel based on mode."""
    color = "green" if mode == "OPERATIONAL" else "cyan"
    icon = "💀" if mode == "OPERATIONAL" else "🤖"
    
    console.print("\n")
    console.print(Panel(
        response,
        title=f"[bold {color}]{icon} KALIROOT AI [{mode}][/bold {color}]",
        border_style=color,
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print("\n")


def clear_screen() -> None:
    """Clear the terminal screen."""
    console.clear()


def get_input(prompt: str = "") -> str:
    """Get user input with styled prompt."""
    return Prompt.ask(f"[bold cyan]?[/bold cyan] {prompt}")


def confirm(message: str) -> bool:
    """Ask for confirmation."""
    return Confirm.ask(f"[bold yellow]?[/bold yellow] {message}")


def show_loading(message: str = "Processing..."):
    """Show professional loading spinner."""
    return console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots")


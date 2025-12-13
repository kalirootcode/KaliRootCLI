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
        >>> ADVANCED SECURITY OPERATIONS CLI v2.0 <<<
    """
    console.print(Panel(
        Text(banner, style="bold cyan", justify="center"),
        box=box.HEAVY,
        border_style="blue",
        title="[bold white]v2.0.0[/bold white]",
        subtitle="[dim]Web Search │ Agent │ Planner[/dim]"
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


def print_ai_response(response: str, mode: str = "CONSULTATION", command: str = None) -> None:
    """
    Print AI response with colored formatting (no panel/frame).
    
    Args:
        response: The AI response text
        mode: CONSULTATION or OPERATIONAL/OPERATIVO
        command: Optional command that was analyzed (shown in blue)
    """
    import re
    
    # Handle both English and Spanish mode names
    is_premium = mode.upper() in ["OPERATIONAL", "OPERATIVO"]
    mode_color = "green" if is_premium else "cyan"
    icon = "💀" if is_premium else "🤖"
    display_mode = "OPERATIVO" if is_premium else "CONSULTA"
    
    console.print()
    
    # Header with command in blue if provided
    if command:
        console.print(f"{icon} [bold blue]{command}[/bold blue] [{mode_color}][{display_mode}][/{mode_color}]")
    else:
        console.print(f"{icon} [bold {mode_color}]KALIROOT AI[/bold {mode_color}] [{mode_color}][{display_mode}][/{mode_color}]")
    
    console.print()
    
    # Process and colorize the response
    lines = response.split('\n')
    
    for line in lines:
        # Section headers (numbered or with **)
        if re.match(r'^\*\*\d+\.', line) or re.match(r'^\d+\.', line):
            # Main section header - yellow
            console.print(f"[bold yellow]{line}[/bold yellow]")
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            # Bold section - cyan
            clean = line.replace('**', '')
            console.print(f"[bold cyan]{clean}[/bold cyan]")
        elif line.strip().startswith('* **'):
            # Sub-item with bold - green bullet
            parts = line.split('**')
            if len(parts) >= 3:
                prefix = parts[0].replace('*', '•')
                key = parts[1]
                rest = ''.join(parts[2:])
                console.print(f"[green]{prefix}[/green][bold white]{key}[/bold white]{rest}")
            else:
                console.print(f"[green]{line}[/green]")
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            # Bullet points - green
            console.print(f"[green]{line}[/green]")
        elif line.strip().startswith('+') or line.strip().startswith('  +'):
            # Sub-bullets - dim cyan
            console.print(f"[dim cyan]{line}[/dim cyan]")
        elif '`' in line:
            # Lines with code/commands - highlight backticks
            # Replace `command` with styled version
            formatted = re.sub(r'`([^`]+)`', r'[bold magenta]\1[/bold magenta]', line)
            console.print(formatted)
        else:
            # Regular text
            console.print(line)
    
    console.print()


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


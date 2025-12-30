"""
Display utilities for KaliRoot CLI
Professional terminal output using Rich library and Pyfiglet.
Modern Purple/Cyan cybersecurity theme.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.style import Style

# Import new color palette
from .colors import (
    STYLE_BLUE, STYLE_BLUE_DARK, STYLE_BLUE_BRIGHT,
    STYLE_CYAN, STYLE_CYAN_BRIGHT, STYLE_CYAN_DARK,
    STYLE_MATRIX_GREEN, STYLE_SUCCESS, STYLE_WARNING, STYLE_ERROR,
    STYLE_TEXT, STYLE_TEXT_DIM,
    GRADIENT_BLUE_CYAN
)

# Try to import pyfiglet
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

# Global console instance
console = Console()


def print_error(message: str) -> None:
    """Print professional error message."""
    console.print(f"[bold {STYLE_ERROR}]❌ ERROR:[/bold {STYLE_ERROR}] [{STYLE_TEXT}]{message}[/{STYLE_TEXT}]")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold {STYLE_SUCCESS}]✅ SUCCESS:[/bold {STYLE_SUCCESS}] [{STYLE_TEXT}]{message}[/{STYLE_TEXT}]")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold {STYLE_WARNING}]⚠️  WARNING:[/bold {STYLE_WARNING}] [{STYLE_TEXT}]{message}[/{STYLE_TEXT}]")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold {STYLE_CYAN}]ℹ️  INFO:[/bold {STYLE_CYAN}] [{STYLE_TEXT}]{message}[/{STYLE_TEXT}]")


def print_banner(show_skull: bool = False) -> None:
    """Print the professional KR-CLI banner (original ASCII with Blue/Cyan gradient)."""
    
    # Original ASCII banner
    banner_ascii = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""
    
    lines = banner_ascii.strip().split("\n")
    
    # Apply Blue→Cyan gradient
    banner_rich = Text()
    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        # Calculate gradient position
        progress = i / max(total_lines - 1, 1)
        color_idx = int(progress * (len(GRADIENT_BLUE_CYAN) - 1))
        color = GRADIENT_BLUE_CYAN[color_idx]
        
        banner_rich.append(line + "\n", style=f"bold {color}")
    
    # Center and display in panel with vertical padding
    centered_banner = Align.center(banner_rich)
    console.print(Panel(
        centered_banner,
        box=box.DOUBLE_EDGE,
        border_style=STYLE_CYAN,
        title=f"[bold {STYLE_TEXT}]💀 DOMINION v3.0 💀[/bold {STYLE_TEXT}]",
        subtitle=f"[italic {STYLE_CYAN}]Advanced AI Security Operations[/italic {STYLE_CYAN}]",
        padding=(1, 4)  # (vertical, horizontal) - increased for better centering
    ))
    
    # Credits line
    credits = Text()
    credits.append("Created by ", style=STYLE_TEXT_DIM)
    credits.append("Sebastian Lara", style=f"bold {STYLE_BLUE}")
    credits.append(" - Security Manager & Developer", style=STYLE_TEXT_DIM)
    console.print(Align.center(credits))
    console.print()


def _get_fallback_banner() -> list:
    """Fallback banner (same as main banner)."""
    return [
        "██╗  ██╗██████╗        ██████╗██╗     ██╗",
        "██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║",
        "█████╔╝ ██████╔╝█████╗██║     ██║     ██║",
        "██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║",
        "██║  ██╗██║  ██║      ╚██████╗███████╗██║",
        "╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝"
    ]


def print_header(title: str) -> None:
    """Print a main section header."""
    console.print(f"\n[bold {STYLE_TEXT} on {STYLE_BLUE_DARK}] ✨ {title.upper()} ✨ [/bold {STYLE_TEXT} on {STYLE_BLUE_DARK}]\n")


def print_divider(title: str = "") -> None:
    """Print a divider with optional title."""
    if title:
        console.print(f"[bold {STYLE_CYAN}]{'─' * 60}[/bold {STYLE_CYAN}]")
    else:
        console.print(f"[{STYLE_CYAN_DIM}]{'─' * 60}[/{STYLE_CYAN_DIM}]")


def print_menu_option(number: str, text: str, description: str = "") -> None:
    """Print a menu option with description."""
    console.print(f" [bold {STYLE_BLUE}]{number}[/bold {STYLE_BLUE}] › [bold {STYLE_TEXT}]{text}[/bold {STYLE_TEXT}]")
    if description:
        console.print(f"    [{STYLE_TEXT_DIM}]{description}[/{STYLE_TEXT_DIM}]")


def print_panel(content: str, title: str = "", style: str = None) -> None:
    """Print content in a panel."""
    border_color = style or STYLE_CYAN
    console.print(Panel(
        f"[{STYLE_TEXT}]{content}[/{STYLE_TEXT}]",
        title=f"[bold {STYLE_BLUE}]{title}[/bold {STYLE_BLUE}]" if title else None,
        border_style=border_color,
        box=box.ROUNDED,
        padding=(1, 2)
    ))


def print_ai_response(response: str, mode: str = "CONSULTATION", command: str = None) -> None:
    """
    Print AI response with colored formatting.
    
    Args:
        response: The AI response text
        mode: CONSULTATION or OPERATIONAL/OPERATIVO
        command: Optional command that was analyzed
    """
    import re
    
    # Handle both English and Spanish mode names
    is_premium = mode.upper() in ["OPERATIONAL", "OPERATIVO"]
    mode_color = STYLE_BLUE if is_premium else STYLE_CYAN
    icon = "💀" if is_premium else "🤖"
    display_mode = "OPERATIVO" if is_premium else "CONSULTA"
    
    console.print()
    
    # Header
    if command:
        console.print(f"{icon} [bold {STYLE_BLUE}]{command}[/bold {STYLE_BLUE}] [{mode_color}][{display_mode}][/{mode_color}]")
    else:
        console.print(f"{icon} [bold {mode_color}]KALIROOT AI[/bold {mode_color}] [{mode_color}][{display_mode}][/{mode_color}]")
    
    console.print()
    
    # Process and colorize the response
    if not isinstance(response, str):
        console.print(f"[{STYLE_TEXT}]{str(response)}[/{STYLE_TEXT}]")
        return

    lines = response.split('\n')
    
    # Keyword highlighter function
    def highlight_keywords(text):
        # 1. Backticks content (commands) → Magenta
        text = re.sub(r'`([^`]+)`', rf'[bold {STYLE_BLUE}]\1[/bold {STYLE_BLUE}]', text)
        
        # 2. Bold markers **text** → Bold White
        text = re.sub(r'\*\*([^*]+)\*\*', rf'[bold {STYLE_TEXT}]\1[/bold {STYLE_TEXT}]', text)
        
        # 3. Technical keywords → Cyan
        keywords = ["apache", "nginx", "openssh", "nmap", "curl", "ubuntu", "linux", "kali", "tcp", "udp", "http", "https", "ssl", "tls"]
        for kw in keywords:
            pattern = re.compile(r'\b(' + re.escape(kw) + r')\b', re.IGNORECASE)
            text = pattern.sub(rf"[{STYLE_CYAN}]\1[/{STYLE_CYAN}]", text)
            
        return text

    for line in lines:
        processed_line = highlight_keywords(line)
        
        # Section headers (numbered)
        if re.match(r'^\d+\.', line):
            clean_line = line.replace('**', '')
            match = re.match(r'^(\d+\.)\s*(.*)', clean_line)
            if match:
                number = match.group(1)
                text = match.group(2)
                styled_text = highlight_keywords(text)
                console.print(f"[bold {STYLE_BLUE_DARK}]{number}[/bold {STYLE_BLUE_DARK}] [{STYLE_TEXT}]{styled_text}[/{STYLE_TEXT}]")
            else:
                console.print(f"[bold {STYLE_BLUE_DARK}]{clean_line}[/bold {STYLE_BLUE_DARK}]")
            
        # Bold Headers
        elif line.strip().startswith('###') or (line.strip().startswith('**') and line.strip().endswith('**')):
            clean = line.replace('**', '').replace('###', '').strip()
            console.print(f"[bold {STYLE_TEXT}]{clean}[/bold {STYLE_TEXT}]")
            
        # List items
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            content = processed_line.lstrip('*- ').strip()
            console.print(f"[{STYLE_CYAN}]•[/{STYLE_CYAN}] [{STYLE_TEXT}]{content}[/{STYLE_TEXT}]")
            
        elif line.strip().startswith('+'):
            content = processed_line.lstrip('+ ').strip()
            console.print(f"  [{STYLE_TEXT_DIM}]›[/{STYLE_TEXT_DIM}] [{STYLE_TEXT}]{content}[/{STYLE_TEXT}]")
            
        else:
            # Regular text
            if line.strip():
                console.print(f"[{STYLE_TEXT}]{processed_line}[/{STYLE_TEXT}]")
            else:
                console.print()
    
    console.print()


def clear_screen() -> None:
    """Clear the terminal screen completely."""
    import os
    import sys
    
    # ANSI escape sequences
    sys.stdout.write('\033[H\033[2J\033[3J')
    sys.stdout.flush()
    
    # System clear command
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear -x 2>/dev/null || clear')
    
    # Rich console clear
    console.clear()


def clear_and_show_banner() -> None:
    """Clear screen and redisplay banner."""
    clear_screen()
    print_banner()


def get_input(prompt: str = "") -> str:
    """Get user input with styled prompt."""
    return Prompt.ask(f"[bold {STYLE_BLUE}]?[/bold {STYLE_BLUE}] [{STYLE_TEXT}]{prompt}[/{STYLE_TEXT}]")


def confirm(message: str) -> bool:
    """Ask for confirmation."""
    return Confirm.ask(f"[bold {STYLE_CYAN}]?[/bold {STYLE_CYAN}] [{STYLE_TEXT}]{message}[/{STYLE_TEXT}]")


def show_loading(message: str = "Processing..."):
    """Show professional loading spinner."""
    return console.status(f"[bold {STYLE_BLUE}]{message}[/bold {STYLE_BLUE}]", spinner="dots")


# Legacy compatibility - keep old variable names pointing to new colors
STYLE_ORANGE_RED = STYLE_BLUE_DARK
STYLE_YELLOW = STYLE_CYAN
STYLE_ORANGE_MAIN = STYLE_BLUE
STYLE_WHITE = STYLE_TEXT
BANNER_ASCII = "\n".join(_get_fallback_banner())

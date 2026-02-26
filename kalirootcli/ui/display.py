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


def stream_ai_response(stream_generator, mode: str = "DOMINION") -> str:
    """
    Stream AI response live — shows tokens as they arrive, then renders
    the final formatted result in a single pass (no style flash).
    Returns the full response text.
    """
    import sys
    import re
    from rich.live import Live
    from rich.text import Text as RichText

    mode_color = STYLE_CYAN
    icon = "⚡"

    # ── Header ──────────────────────────────────────────────────────────
    console.print()
    header = RichText()
    header.append(f" {icon} ", style="bold white")
    header.append("DOMINION AI", style=f"bold {mode_color}")
    header.append("  ─── streaming", style=f"dim {STYLE_BLUE}")
    console.print(header)
    console.print(f"[{STYLE_BLUE_DARK}]{'─' * 60}[/{STYLE_BLUE_DARK}]")

    # ── Stream tokens live ──────────────────────────────────────────────
    full_text = ""
    streaming_text = RichText()

    with Live(streaming_text, console=console, refresh_per_second=15, transient=True) as live:
        for chunk in stream_generator:
            full_text += chunk
            streaming_text = RichText(full_text, style=f"{STYLE_CYAN}")
            live.update(streaming_text)

    # ── Final render (single pass — no flash) ───────────────────────────
    if full_text:
        print_ai_response(full_text, mode)

    return full_text


def print_ai_response(response: str, mode: str = "CONSULTATION", command: str = None) -> None:
    """
    Professional AI response renderer — DOMINION Edition.
    Strips any Rich/bracket markup, then renders clean markdown-style output
    with syntax-highlighted code blocks (editor/cat style).
    Uses logo colors: Deep Blue → Electric Blue → Cyan.
    """
    import re
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.text import Text

    if not isinstance(response, str) or not response.strip():
        console.print(f"[{STYLE_TEXT}]{str(response)}[/{STYLE_TEXT}]")
        return

    # ── 1. Strip ALL Rich/bracket markup ────────────────────────────────
    clean = re.sub(r'\[/?[a-zA-Z][a-zA-Z0-9 _#(),.]*\]', '', response)
    clean = re.sub(r'\[dim\].*?\[/dim\]', '', clean, flags=re.DOTALL)

    # ── 2. Parse and render ─────────────────────────────────────────────
    lines = clean.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Code block: ```lang ... ``` ─────────────────────────────────
        if stripped.startswith('```'):
            lang = stripped[3:].strip() or "text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```

            code_text = '\n'.join(code_lines)
            if code_text.strip():
                console.print()
                console.print(Panel(
                    Syntax(code_text, lang, theme="monokai", line_numbers=True,
                           word_wrap=True, padding=(0, 1)),
                    title=f"[bold {STYLE_CYAN}] 📄 {lang.upper()} [/bold {STYLE_CYAN}]",
                    subtitle=f"[dim {STYLE_BLUE_DARK}]DOMINION[/dim {STYLE_BLUE_DARK}]",
                    border_style=STYLE_BLUE,
                    padding=(0, 0),
                ))
                console.print()
            continue

        # ── H1/H2/H3 headers ───────────────────────────────────────────
        if stripped.startswith('###'):
            title = stripped.lstrip('#').strip()
            console.print(f"\n  [bold {STYLE_CYAN}]▸ {title}[/bold {STYLE_CYAN}]")
            i += 1
            continue

        if stripped.startswith('##'):
            title = stripped.lstrip('#').strip()
            console.print(f"\n[bold {STYLE_BLUE}]━━ {title} ━━[/bold {STYLE_BLUE}]")
            i += 1
            continue

        if stripped.startswith('#'):
            title = stripped.lstrip('#').strip()
            console.print(f"\n[bold white on {STYLE_BLUE_DARK}] ◆ {title.upper()} [/bold white on {STYLE_BLUE_DARK}]")
            i += 1
            continue

        # ── Bold-only line: **title** ───────────────────────────────────
        if stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
            title = stripped[2:-2]
            console.print(f"\n  [bold white]{title}[/bold white]")
            i += 1
            continue

        # ── Numbered sections: 1. Title ─────────────────────────────────
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            num = num_match.group(1)
            text = _render_inline(num_match.group(2))
            console.print(f"\n [bold {STYLE_CYAN}]{num}.[/bold {STYLE_CYAN}] [bold white]{text}[/bold white]")
            i += 1
            continue

        # ── Bullet lists: - or * ────────────────────────────────────────
        if stripped.startswith('- ') or stripped.startswith('* '):
            indent = len(line) - len(line.lstrip())
            content = _render_inline(stripped[2:])
            prefix = "  " * (indent // 2)
            console.print(f"{prefix} [{STYLE_BLUE}]•[/{STYLE_BLUE}] [{STYLE_TEXT}]{content}[/{STYLE_TEXT}]")
            i += 1
            continue

        # ── Sub-bullets ─────────────────────────────────────────────────
        if stripped.startswith('+ '):
            content = _render_inline(stripped[2:])
            console.print(f"    [{STYLE_TEXT_DIM}]›[/{STYLE_TEXT_DIM}] [{STYLE_TEXT}]{content}[/{STYLE_TEXT}]")
            i += 1
            continue

        # ── Horizontal rule ─────────────────────────────────────────────
        if stripped in ('---', '***', '___'):
            console.print(f"[{STYLE_BLUE_DARK}]{'─' * 50}[/{STYLE_BLUE_DARK}]")
            i += 1
            continue

        # ── Regular text ────────────────────────────────────────────────
        if stripped:
            console.print(f"  [{STYLE_TEXT}]{_render_inline(stripped)}[/{STYLE_TEXT}]")
        else:
            console.print()

        i += 1

    console.print(f"[{STYLE_BLUE_DARK}]{'─' * 60}[/{STYLE_BLUE_DARK}]")
    console.print()


def _render_inline(text: str) -> str:
    """Render inline markdown: **bold**, `code`."""
    import re

    # 1. Inline code `command` → bright blue
    text = re.sub(r'`([^`]+)`', rf'[bold {STYLE_CYAN}]\1[/bold {STYLE_CYAN}]', text)

    # 2. Bold **text** → bold white
    text = re.sub(r'\*\*([^*]+)\*\*', rf'[bold white]\1[/bold white]', text)

    # 3. Italic *text*
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', rf'[italic {STYLE_TEXT_DIM}]\1[/italic {STYLE_TEXT_DIM}]', text)

    return text



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


def print_system_status_panel(
    system_info: dict = None,
    is_premium: bool = False,
    days_remaining: int = 0,
    credits: int = 0
) -> None:
    """
    Print a hacker-style system status panel.
    
    Args:
        system_info: Dictionary from SystemCollector.get_display_summary()
        is_premium: Whether user is premium
        days_remaining: Days remaining in premium subscription
        credits: Current credit balance
    """
    from rich.table import Table
    
    if not system_info:
        # Import and collect if not provided
        try:
            from ..system_collector import system_collector
            system_collector.collect(include_ip=True)
            system_info = system_collector.get_display_summary()
        except Exception:
            system_info = {
                "ip": "Unknown",
                "vpn_status": "⚠️ UNKNOWN",
                "os": "Unknown OS",
                "cpu": "Unknown CPU",
                "ram": "? GB",
                "hostname": "unknown",
                "distro": "Unknown"
            }
    
    # Build the panel content
    content = Text()
    
    # Header line
    content.append("◢◤ SYSTEM STATUS ◥◣\n\n", style=f"bold {STYLE_CYAN_BRIGHT}")
    
    # Network section
    content.append("  🌐 ", style="white")
    content.append("IP: ", style=STYLE_TEXT_DIM)
    content.append(f"{system_info.get('ip', 'Unknown')}\n", style=f"bold {STYLE_CYAN}")
    
    # VPN Status
    vpn_status = system_info.get('vpn_status', 'UNKNOWN')
    vpn_interface = system_info.get('vpn_interface', '')
    content.append("  ", style="white")
    if 'ACTIVE' in vpn_status.upper():
        content.append("🔒 ", style="white")
        content.append("VPN: ", style=STYLE_TEXT_DIM)
        content.append(f"ACTIVE", style=f"bold {STYLE_SUCCESS}")
        if vpn_interface:
            content.append(f" ({vpn_interface})", style=STYLE_TEXT_DIM)
    else:
        content.append("⚠️ ", style="white")
        content.append("VPN: ", style=STYLE_TEXT_DIM)
        content.append("NOT DETECTED", style=f"bold {STYLE_WARNING}")
    content.append("\n", style="white")
    
    # OS Info
    content.append("  💻 ", style="white")
    content.append(f"{system_info.get('os', 'Unknown OS')}\n", style=STYLE_TEXT)
    
    # Hardware
    content.append("  🧠 ", style="white")
    cpu = system_info.get('cpu', 'Unknown')
    # Truncate long CPU names
    if len(cpu) > 35:
        cpu = cpu[:32] + "..."
    content.append(f"{cpu}\n", style=STYLE_TEXT_DIM)
    
    content.append("  💾 ", style="white")
    content.append(f"RAM: {system_info.get('ram', '?')} GB\n", style=STYLE_TEXT_DIM)
    
    # Divider
    content.append("\n  ", style="white")
    content.append("━" * 38 + "\n\n", style=STYLE_BLUE_DARK)
    
    # Subscription Status
    if is_premium:
        content.append("  👑 ", style="white")
        content.append("PREMIUM", style=f"bold {STYLE_SUCCESS}")
        content.append(" | ", style=STYLE_TEXT_DIM)
        content.append(f"{days_remaining} días restantes\n", style=f"bold {STYLE_CYAN}")
    else:
        content.append("  📊 ", style="white")
        content.append("FREE", style=f"bold {STYLE_WARNING}")
        content.append(" | ", style=STYLE_TEXT_DIM)
        content.append(f"{credits} créditos\n", style=f"bold {STYLE_CYAN}")
    
    # Print the panel
    console.print(Panel(
        content,
        box=box.DOUBLE,
        border_style=STYLE_BLUE_DARK,
        padding=(1, 2)
    ))


def print_compact_system_status(
    system_info: dict = None,
    is_premium: bool = False,
    days_remaining: int = 0,
    credits: int = 0
) -> None:
    """
    Print a compact one-line system status bar.
    
    Args:
        system_info: Dictionary from SystemCollector.get_display_summary()
        is_premium: Whether user is premium
        days_remaining: Days remaining in premium subscription
        credits: Current credit balance
    """
    if not system_info:
        try:
            from ..system_collector import system_collector
            if system_collector.info is None:
                system_collector.collect(include_ip=False)  # Don't delay with IP fetch
            system_info = system_collector.get_display_summary()
        except Exception:
            system_info = {"vpn_status": "?", "distro": "Unknown"}
    
    status = Text()
    
    # VPN indicator
    if 'ACTIVE' in system_info.get('vpn_status', '').upper():
        status.append("🔒 VPN ", style=f"bold {STYLE_SUCCESS}")
    else:
        status.append("⚠️ NO VPN ", style=f"bold {STYLE_WARNING}")
    
    status.append("│ ", style=STYLE_TEXT_DIM)
    
    # Distro
    status.append(f"{system_info.get('distro', '?')} ", style=STYLE_TEXT)
    
    status.append("│ ", style=STYLE_TEXT_DIM)
    
    # Subscription
    if is_premium:
        status.append(f"👑 PREMIUM ({days_remaining}d)", style=f"bold {STYLE_SUCCESS}")
    else:
        status.append(f"💳 {credits} créditos", style=f"bold {STYLE_CYAN}")
    
    console.print(Align.center(status))


# Legacy compatibility - keep old variable names pointing to new colors
STYLE_ORANGE_RED = STYLE_BLUE_DARK
STYLE_YELLOW = STYLE_CYAN
STYLE_ORANGE_MAIN = STYLE_BLUE
STYLE_WHITE = STYLE_TEXT
BANNER_ASCII = "\n".join(_get_fallback_banner())


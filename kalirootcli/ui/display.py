"""
Display utilities for KaliRoot CLI
Professional terminal output using Rich library.
Enhanced with pyfiglet and theme colors from logo.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.style import Style

# Try to import pyfiglet
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

# Global console instance
console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# THEME COLORS (Based on skull image)
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# THEME COLORS (Based on skull image - Orange Dominion)
# ═══════════════════════════════════════════════════════════════════════════════
STYLE_BG = "rgb(0,0,0)"              # Black background
STYLE_WHITE = "rgb(255,255,255)"      # White - main skull
STYLE_ORANGE_RED = "rgb(255,69,0)"    # Orange-Red - glitch top
STYLE_YELLOW = "rgb(255,165,0)"       # Yellow-Orange - transition
STYLE_CYAN = "rgb(0,206,209)"         # Cyan - glitch bottom
STYLE_ORANGE_MAIN = "rgb(255,140,0)"  # Main Orange for UI
STYLE_PINK = "rgb(255,105,180)"       # Pink accent (optional)

# Legacy aliases for compatibility
STYLE_RED = STYLE_ORANGE_RED
STYLE_ORANGE = STYLE_YELLOW


def print_error(message: str) -> None:
    """Print professional error message."""
    console.print(f"[bold {STYLE_ORANGE_RED}]❌ ERROR:[/bold {STYLE_ORANGE_RED}] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[bold green]✅ SUCCESS:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[bold {STYLE_YELLOW}]⚠️  WARNING:[/bold {STYLE_YELLOW}] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[bold {STYLE_YELLOW}]ℹ️  INFO:[/bold {STYLE_YELLOW}] {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# BANNER ASSETS
# ═══════════════════════════════════════════════════════════════════════════════

SKULL_SMALL = r"""
                    ..........        ...               
            .',:;.',''..,:cllllllc;'.    .,'. ....          
            ''lXO,.,,:lx0XWMMMMMMWNKko;..''cxl.....         
           ..,OMWKxdkXMMMMMMMMMMMMMMMMN0ddONMWl..           
            .'OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc..           
              ,OWMMMMMMMMMMMMMMMMMMMMMMMMMMMXl'.            
           ....'oXMMMWWWWWWMMMMMMWWWWWWWMMWO;,;'.           
           .'',..lXOccccccclKMMNxcccccccdXNc.',,'..         
             ...'dK:......,.dMM0,.....','dO;.,'...          
                .':l,....',;cccc:. ...',lc..'''.            
               .'.oNKdlllodc''..,oollloONO,....             
           ......;xkkkXMMWx,,. ..cXMWMMMMMO'.               
           ........;lxKMMWx,'..''cKMMMMN0xc;,.              
               ...,;;oXMMMWKOOkO0NMMMWOc;,''                
               .',;;,.cXMNk0MMMMXx00dl..,.                  
                 ......cKXclWMMMk;xO;.''..                  
                       .;c,,oxkx:'cl:;.                     
                        .......''''..           
"""

BANNER_ASCII = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""

def print_banner(show_skull: bool = False) -> None:
    """Print the professional KR-CLI banner (DOMINION Edition) with Skull."""
    
    if show_skull:
        # 1. Render Skull
        skull_lines = SKULL_SMALL.strip().split('\n')
        skull_text = Text()
        
        for i, line in enumerate(skull_lines):
            progress = i / max(len(skull_lines) - 1, 1)
            if progress < 0.3:
                style = STYLE_ORANGE_RED
            elif progress < 0.7:
                style = STYLE_WHITE
            else:
                style = STYLE_CYAN
            skull_text.append(line + "\n", style=style)
            
        centered_skull = Align.center(skull_text)
        console.print(centered_skull)

    # 2. Render Text Banner (Always needed)
    banner_lines = BANNER_ASCII.strip().split("\n")
    banner_text = Text()
    
    total_lines = len(banner_lines)
    for i, line in enumerate(banner_lines):
        progress = i / max(total_lines - 1, 1)
        # Gradient: red -> orange -> cyan (Match splash screen)
        if progress < 0.33:
            style = f"bold {STYLE_ORANGE_RED}"
        elif progress < 0.66:
            style = f"bold {STYLE_YELLOW}"
        else:
            style = f"bold {STYLE_CYAN}"
        banner_text.append(line + "\n", style=style)
    
    centered_banner = Align.center(banner_text)
    console.print(Panel(
        centered_banner,
        box=box.DOUBLE_EDGE,
        border_style=STYLE_ORANGE_RED,
        title=f"[bold white]💀 DOMINION v3.0 💀[/bold white]",
        subtitle=f"[italic {STYLE_ORANGE_MAIN}]Advanced AI Security Operations[/italic {STYLE_ORANGE_MAIN}]",
        padding=(0, 2)
    ))
    
    # Credits line
    credits = Text()
    credits.append("Created by ", style="dim")
    credits.append("Sebastian Lara", style=f"bold {STYLE_ORANGE_MAIN}")
    credits.append(" - Security Manager & Developer", style="dim")
    console.print(Align.center(credits))
    console.print()

    
def print_header(title: str) -> None:
    """Print a main section header (Gemini Style)."""
    # Orange Red background (User request)
    console.print(f"\n[bold white on {STYLE_ORANGE_RED}] ✨ {title.upper()} ✨ [/bold white on {STYLE_ORANGE_RED}]\n")

def print_divider(title: str = "") -> None:
    """Print a divider with optional title."""
    if title:
        console.rule(f"[bold {STYLE_YELLOW}]{title}[/bold {STYLE_YELLOW}]", style=f"{STYLE_ORANGE_RED}")
    else:
        console.rule(style=f"dim {STYLE_ORANGE_RED}")


def print_menu_option(number: str, text: str, description: str = "") -> None:
    """Print a menu option with description."""
    console.print(f" [bold {STYLE_ORANGE_MAIN}]{number}[/bold {STYLE_ORANGE_MAIN}] › [white bold]{text}[/white bold]")
    if description:
        console.print(f"    [dim]{description}[/dim]")


def print_panel(content: str, title: str = "", style: str = STYLE_ORANGE_RED) -> None:
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
    mode_color = "green" if is_premium else "yellow"
    icon = "💀" if is_premium else "🤖"
    display_mode = "OPERATIVO" if is_premium else "CONSULTA"
    
    console.print()
    
    # Header with command in orange if provided
    if command:
        console.print(f"{icon} [bold {STYLE_ORANGE_MAIN}]{command}[/bold {STYLE_ORANGE_MAIN}] [{mode_color}][{display_mode}][/{mode_color}]")
    else:
        console.print(f"{icon} [bold {mode_color}]KALIROOT AI[/bold {mode_color}] [{mode_color}][{display_mode}][/{mode_color}]")
    
    console.print()
    
    # Process and colorize the response
    lines = response.split('\n')
    
    for line in lines:
        # Section headers (numbered or with **)
        if re.match(r'^\*\*\d+\.', line) or re.match(r'^\d+\.', line):
            # Main section header - orange-red
            console.print(f"[bold {STYLE_ORANGE_RED}]{line}[/bold {STYLE_ORANGE_RED}]")
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            # Bold section - yellow
            clean = line.replace('**', '')
            console.print(f"[bold {STYLE_YELLOW}]{clean}[/bold {STYLE_YELLOW}]")
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
            # Sub-bullets - dim yellow
            console.print(f"[dim {STYLE_YELLOW}]{line}[/dim {STYLE_YELLOW}]")
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


def clear_and_show_banner() -> None:
    """Clear screen and redisplay banner (for menu returns)."""
    console.clear()
    print_banner()


def get_input(prompt: str = "") -> str:
    """Get user input with styled prompt."""
    return Prompt.ask(f"[bold {STYLE_ORANGE_MAIN}]?[/bold {STYLE_ORANGE_MAIN}] {prompt}")


def confirm(message: str) -> bool:
    """Ask for confirmation."""
    return Confirm.ask(f"[bold {STYLE_YELLOW}]?[/bold {STYLE_YELLOW}] {message}")


def show_loading(message: str = "Processing..."):
    """Show professional loading spinner."""
    return console.status(f"[bold {STYLE_ORANGE_MAIN}]{message}[/bold {STYLE_ORANGE_MAIN}]", spinner="dots")

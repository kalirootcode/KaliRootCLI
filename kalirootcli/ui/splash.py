import time
import shutil
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.live import Live

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

console = Console()


def _clear_terminal() -> None:
    """
    Clear the terminal COMPLETELY - no trace left.
    Uses ANSI escape sequences and system commands.
    """
    import os
    import sys
    
    # ANSI escape sequences for complete clear
    sys.stdout.write('\033[H\033[2J\033[3J')
    sys.stdout.flush()
    
    # System clear command
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear -x 2>/dev/null || clear')
    
    # Rich console clear
    console.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Based on skull image)
# ═══════════════════════════════════════════════════════════════════════════════
STYLE_BG = "rgb(0,0,0)"              # Black background
STYLE_WHITE = "rgb(255,255,255)"      # White - main skull
STYLE_ORANGE_RED = "rgb(255,69,0)"    # Orange-Red - glitch top
STYLE_YELLOW = "rgb(255,165,0)"       # Yellow-Orange - transition
STYLE_CYAN = "rgb(0,206,209)"         # Cyan - glitch bottom
STYLE_PINK = "rgb(255,105,180)"       # Pink accent (optional)


# ═══════════════════════════════════════════════════════════════════════════════
# SKULL LOGO (Recreation of banner.txt - proper size)
# ═══════════════════════════════════════════════════════════════════════════════

# Devil skull with horns - recreated from banner.txt at proper size
SKULL_LOGO = r"""
              ......    ..........        ...               
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

# Smaller version for small terminals
SKULL_SMALL = r"""
        ......    ..........        ...               
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


def get_terminal_size() -> tuple:
    """Get current terminal size."""
    size = shutil.get_terminal_size((80, 24))
    return max(size.columns, 60), max(size.lines, 20)


def get_skull_logo() -> str:
    """Get appropriate skull logo based on terminal size."""
    term_width, term_height = get_terminal_size()
    
    if term_width >= 70 and term_height >= 25:
        return SKULL_LOGO
    else:
        return SKULL_SMALL


def render_skull_text(term_width: int) -> Text:
    """Render skull logo as Rich Text with colors."""
    skull = get_skull_logo()
    lines = skull.strip().split('\n')
    
    result = Text()
    total = len(lines)
    
    for i, line in enumerate(lines):
        progress = i / max(total - 1, 1)
        
        # Center the line
        padding = max(0, (term_width - len(line)) // 2)
        centered_line = " " * padding + line
        
        # Apply gradient: orange-red (top) -> white (middle) -> cyan (bottom)
        if progress < 0.3:
            result.append(centered_line + "\n", style=f"bold {STYLE_ORANGE_RED}")
        elif progress < 0.7:
            result.append(centered_line + "\n", style=f"bold {STYLE_WHITE}")
        else:
            result.append(centered_line + "\n", style=f"bold {STYLE_CYAN}")
    
    return result


def render_kr_cli_banner(term_width: int) -> Text:
    """Render KR-CLI text with high-quality custom ASCII."""
    from .display import BANNER_ASCII
    
    # Use the shared banner constant
    # Strip leading newlines but preserve internal relative layout
    lines = [line for line in BANNER_ASCII.split("\n") if line.strip()]
    
    # Calculate dimensions
    max_line_width = max(len(line) for line in lines) if lines else 0
    padding = max(0, (term_width - max_line_width) // 2)
    
    result = Text()
    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        # Apply the SAME global padding to every line to keep them aligned
        centered = " " * padding + line
        
        # Apply strict 3-color gradient
        # Top = Orange-Red
        # Middle = Yellow
        # Bottom = Cyan
        if i < total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_ORANGE_RED}")
        elif i < 2 * total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_YELLOW}")
        else:
            result.append(centered + "\n", style=f"bold {STYLE_CYAN}")
    
    return result


def create_loading_display(progress_pct: float, term_width: int, status: str) -> Text:
    """Create loading bar display."""
    bar_width = min(50, term_width - 20)
    filled = int(bar_width * progress_pct)
    empty = bar_width - filled
    
    # Build bar
    bar = "█" * filled + "▒" * empty
    pct = f"{int(progress_pct * 100):3d}%"
    
    result = Text()
    
    # Center the loading bar
    line = f"  ⟨ {bar} ⟩  {pct}"
    padding = max(0, (term_width - len(line)) // 2)
    
    result.append(" " * padding)
    result.append("  ⟨ ", style=STYLE_CYAN)
    result.append("█" * filled, style=f"bold {STYLE_YELLOW}")
    result.append("▒" * empty, style="dim white")
    result.append(" ⟩  ", style=STYLE_CYAN)
    result.append(pct, style=f"bold {STYLE_WHITE}")
    result.append("\n\n")
    
    # Status text
    status_padding = max(0, (term_width - len(status)) // 2)
    result.append(" " * status_padding)
    result.append(status, style=f"italic {STYLE_CYAN}")
    
    return result


def animated_splash(skip_animation: bool = False, duration: float = 5.0) -> None:
    """
    Main animated splash screen with professional presentation.
    Features fade-in effects, perfect centering, and polished animations.
    
    Args:
        skip_animation: If True, shows static version
        duration: Duration of loading animation in seconds (default 5)
    """
    # Clear screen first
    _clear_terminal()
    
    if skip_animation:
        _show_static_splash()
        return
    
    # Get terminal size
    term_width, term_height = get_terminal_size()
    
    # Pre-render all static elements
    skull = get_skull_logo()
    skull_lines = skull.strip().split('\n')
    
    # KR-CLI banner
    # IMPORT RAW BANNER directly to avoid stripping/padding issues
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Calculate max width for centering
    max_logo_width = max(len(line) for line in skull_lines)
    
    # Subtitle elements
    sub_line = "═" * 50
    title_text = "⚡  DOMINION v3.0  ⚡"
    desc_text = "Advanced AI Security Operations"
    
    # Calculate total content height
    skull_height = len(skull_lines)
    kr_height = len(kr_lines)
    subtitle_height = 4
    loading_height = 4
    spacing = 3
    total_content_height = skull_height + spacing + kr_height + spacing + subtitle_height + spacing + loading_height
    
    # Vertical centering
    top_padding = max(0, (term_height - total_content_height) // 2)
    
    # Phase 1: Fade-in animation for logo (0.8 seconds)
    fade_duration = 0.8
    fade_start = time.time()
    
    # Pre-calculate padding for consistency
    max_skull_width = max(len(line) for line in skull_lines) if skull_lines else 0
    skull_padding = max(0, (term_width - max_skull_width) // 2)

    with Live(console=console, refresh_per_second=30, screen=True) as live:
        # Fade in logo
        while time.time() - fade_start < fade_duration:
            elapsed = time.time() - fade_start
            fade_progress = min(elapsed / fade_duration, 1.0)
            
            output = Text()
            output.append("\n" * top_padding)
            
            # Show progressively more lines with fade effect
            visible_lines = int(len(skull_lines) * fade_progress)
            
            for i in range(visible_lines):
                line = skull_lines[i]
                progress = i / max(len(skull_lines) - 1, 1)
                
                # Center the line using BLOCK padding
                
                # Apply gradient coloring
                if progress < 0.3:
                    style = STYLE_ORANGE_RED
                elif progress < 0.7:
                    style = STYLE_WHITE
                else:
                    style = STYLE_CYAN
                
                output.append(" " * skull_padding + line + "\n", style=style)
            
            live.update(output)
            time.sleep(0.03)
        
        # Show complete logo briefly
        time.sleep(0.2)
        
        # Phase 2: Main animation with all elements (remaining duration)
        main_start = time.time()
        main_duration = duration - fade_duration - 0.2
        
        while True:
            elapsed = time.time() - main_start
            progress = min(elapsed / main_duration, 1.0)
            
            output = Text()
            
            # Top padding for vertical centering
            output.append("\n" * top_padding)
            
            # === SKULL LOGO (block centered) ===
            # Calculate skull padding once
            max_skull_width = max(len(line) for line in skull_lines) if skull_lines else 0
            skull_padding = max(0, (term_width - max_skull_width) // 2)
            
            for i, line in enumerate(skull_lines):
                line_progress = i / max(len(skull_lines) - 1, 1)
                
                # Apply gradient coloring
                if line_progress < 0.3:
                    style = STYLE_ORANGE_RED
                elif line_progress < 0.7:
                    style = STYLE_WHITE
                else:
                    style = STYLE_CYAN
                
                output.append(" " * skull_padding + line + "\n", style=style)
            
            output.append("\n")
            
            # === KR-CLI TEXT (block centered) ===
            # Calculate banner padding once
            max_kr_width = max(len(line) for line in kr_lines) if kr_lines else 0
            kr_padding = max(0, (term_width - max_kr_width) // 2)
            
            for i, line in enumerate(kr_lines):
                line_progress = i / max(len(kr_lines) - 1, 1)
                
                if line_progress < 0.33:
                    style = f"bold {STYLE_ORANGE_RED}"
                elif line_progress < 0.66:
                    style = f"bold {STYLE_YELLOW}"
                else:
                    style = f"bold {STYLE_CYAN}"
                
                output.append(" " * kr_padding + line + "\n", style=style)
            
            output.append("\n")
            
            # === SUBTITLE BOX (perfectly centered) ===
            sub_padding = max(0, (term_width - len(sub_line)) // 2)
            title_padding = max(0, (term_width - len(title_text)) // 2)
            desc_padding = max(0, (term_width - len(desc_text)) // 2)
            
            output.append(" " * sub_padding + sub_line + "\n", style=STYLE_ORANGE_RED)
            output.append(" " * title_padding, style="")
            output.append("⚡  ", style=STYLE_YELLOW)
            output.append("DOMINION", style="bold white")
            output.append(" v3.0  ⚡\n", style=STYLE_YELLOW)
            output.append(" " * desc_padding + desc_text + "\n", style=f"italic {STYLE_CYAN}")
            output.append(" " * sub_padding + sub_line + "\n", style=STYLE_ORANGE_RED)
            
            output.append("\n")
            
            # === LOADING BAR (enhanced professional style) ===
            bar_width = 45
            filled = int(bar_width * progress)
            empty = bar_width - filled
            
            # Status text based on progress
            if progress < 0.2:
                status = "⚙  Initializing System"
                status_color = STYLE_CYAN
            elif progress < 0.4:
                status = "📦  Loading Core Modules"
                status_color = STYLE_YELLOW
            elif progress < 0.6:
                status = "🔌  Establishing Connection"
                status_color = STYLE_ORANGE_RED
            elif progress < 0.8:
                status = "🔐  Securing Channel"
                status_color = STYLE_CYAN
            elif progress < 1.0:
                status = "✨  Finalizing Setup"
                status_color = STYLE_YELLOW
            else:
                status = "✓  Ready to Launch"
                status_color = "bold green"
            
            # Progress percentage
            pct = f"{int(progress * 100)}%"
            
            # Build loading bar line
            bar_char_filled = "█"
            bar_char_empty = "░"
            bar_display = bar_char_filled * filled + bar_char_empty * empty
            
            loading_line = f"  ╠ {bar_display} ╣  {pct:>4}"
            loading_padding = max(0, (term_width - len(loading_line)) // 2)
            
            output.append(" " * loading_padding + "  ╠ ", style="dim white")
            output.append(bar_char_filled * filled, style=f"bold {STYLE_YELLOW}")
            output.append(bar_char_empty * empty, style="dim white")
            output.append(" ╣  ", style="dim white")
            output.append(pct, style=f"bold {STYLE_WHITE}")
            output.append("\n\n")
            
            # Status message (centered)
            status_padding = max(0, (term_width - len(status)) // 2)
            output.append(" " * status_padding + status, style=f"{status_color}")
            
            live.update(output)
            
            if progress >= 1.0:
                time.sleep(0.6)
                break
            
            time.sleep(0.04)
    
    # Final clear
    _clear_terminal()


def _show_static_splash() -> None:
    """Show static splash without animation - fully centered."""
    _clear_terminal()
    
    term_width, term_height = get_terminal_size()
    
    # Get logo
    skull = get_skull_logo()
    skull_lines = skull.strip().split('\n')
    
    # IMPORT RAW BANNER
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Render all elements
    output = Text()
    
    # Calculate vertical centering
    skull_height = len(skull_lines)
    kr_height = len(kr_lines)
    subtitle_height = 4
    total_height = skull_height + 2 + kr_height + 2 + subtitle_height
    top_padding = max(0, (term_height - total_height) // 2)
    
    output.append("\n" * top_padding)
    
    # Skull logo (centered with gradient)
    # Calculate skull padding once
    max_skull_width = max(len(line) for line in skull_lines) if skull_lines else 0
    skull_padding = max(0, (term_width - max_skull_width) // 2)
    
    for i, line in enumerate(skull_lines):
        progress = i / max(len(skull_lines) - 1, 1)
        
        if progress < 0.3:
            style = STYLE_ORANGE_RED
        elif progress < 0.7:
            style = STYLE_WHITE
        else:
            style = STYLE_CYAN
        
        output.append(" " * skull_padding + line + "\n", style=style)
    
    output.append("\n")
    
    # KR-CLI (Block centered logic fixed)
    # Calculate banner padding once
    max_kr_width = max(len(line) for line in kr_lines) if kr_lines else 0
    kr_padding = max(0, (term_width - max_kr_width) // 2)

    for i, line in enumerate(kr_lines):
        line_progress = i / max(len(kr_lines) - 1, 1)
        if line_progress < 0.33:
            style = f"bold {STYLE_ORANGE_RED}"
        elif line_progress < 0.66:
            style = f"bold {STYLE_YELLOW}"
        else:
            style = f"bold {STYLE_CYAN}"
            
        output.append(" " * kr_padding + line + "\n", style=style)

    output.append("\n")
    
    # Subtitle
    sub_line = "═" * 50
    title_text = "⚡  DOMINION v3.0  ⚡"
    desc_text = "Advanced AI Security Operations"
    
    sub_padding = max(0, (term_width - len(sub_line)) // 2)
    title_padding = max(0, (term_width - len(title_text)) // 2)
    desc_padding = max(0, (term_width - len(desc_text)) // 2)
    
    output.append(" " * sub_padding + sub_line + "\n", style=STYLE_ORANGE_RED)
    output.append(" " * title_padding, style="")
    output.append("⚡  ", style=STYLE_YELLOW)
    output.append("DOMINION", style="bold white")
    output.append(" v3.0  ⚡\n", style=STYLE_YELLOW)
    output.append(" " * desc_padding + desc_text + "\n", style=f"italic {STYLE_CYAN}")
    output.append(" " * sub_padding + sub_line, style=STYLE_ORANGE_RED)
    
    console.print(output)
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# THEME UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_style_red() -> str:
    return STYLE_ORANGE_RED

def get_style_orange() -> str:
    return STYLE_YELLOW

def get_style_cyan() -> str:
    return STYLE_CYAN

def get_style_pink() -> str:
    return STYLE_PINK


# Test
if __name__ == "__main__":
    animated_splash(duration=5.0)

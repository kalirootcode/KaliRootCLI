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
# COLOR PALETTE (Professional Blue/Cyan/Red Hacker Theme)
# ═══════════════════════════════════════════════════════════════════════════════
STYLE_BG = "rgb(10,10,10)"              # Deep black background
STYLE_WHITE = "rgb(255,255,255)"        # Pure white
STYLE_RED = "rgb(255,50,50)"            # Vibrant red - accent color
STYLE_RED_BRIGHT = "rgb(255,100,100)"   # Bright red
STYLE_BLUE_DARK = "rgb(0,50,150)"       # Dark blue - top accent
STYLE_BLUE = "rgb(0,100,255)"           # Electric blue - middle
STYLE_CYAN = "rgb(0,240,240)"           # Electric cyan - bottom accent
STYLE_CYAN_BRIGHT = "rgb(0,255,255)"    # Bright cyan


# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX RAIN ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════

def matrix_rain_animation(duration: float = 2.0) -> None:
    """
    Professional Matrix-style rain animation with blue-cyan gradient.
    Features:
    - Full screen coverage with dense character rain
    - Smooth blue → cyan gradient (no red)
    - Characters morph/change as they fall
    - Optimized for terminal performance
    
    Args:
        duration: Animation duration in seconds
    """
    import random
    import os
    
    term_width, term_height = get_terminal_size()
    
    # Expanded character set for variety - mix of symbols, numbers, and katakana
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
            "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ" \
            "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    
    # Create DENSE columns (every column for full coverage)
    columns = []
    for x in range(0, term_width):
        columns.append({
            'x': x,
            'y': float(random.randint(-50, -5)),      # Staggered start
            'speed': random.uniform(0.8, 2.2),        # Varied speeds
            'length': random.randint(8, 25),          # Varied trail lengths
            'chars': [random.choice(chars) for _ in range(30)]  # Pre-generate morphing chars
        })
    
    start_time = time.time()
    frame_count = 0
    
    # Adaptive refresh rate
    refresh_rate = 20 if os.environ.get('TERM', '').startswith('xterm') else 15
    
    with Live(console=console, refresh_per_second=refresh_rate, screen=True) as live:
        while time.time() - start_time < duration:
            output = Text()
            
            # Build frame
            frame = [[' ' for _ in range(term_width)] for _ in range(term_height)]
            frame_colors = [[None for _ in range(term_width)] for _ in range(term_height)]
            
            # Update and draw each column
            for col in columns:
                x = col['x']
                if x >= term_width:
                    continue
                    
                head_y = int(col['y'])
                length = col['length']
                
                # Draw trail with morphing characters
                for i in range(length):
                    y_pos = head_y - i
                    
                    if 0 <= y_pos < term_height:
                        # Character morphing: use different char from pre-generated list
                        char_index = (frame_count + i) % len(col['chars'])
                        char_to_draw = col['chars'][char_index]
                        frame[y_pos][x] = char_to_draw
                        
                        # BLUE → CYAN GRADIENT (no red)
                        # Position in trail (0 = head, 1 = tail)
                        trail_progress = i / max(length - 1, 1)
                        
                        if i == 0:
                            # Head: Bright white/cyan
                            frame_colors[y_pos][x] = "bright_white"
                        elif i < 3:
                            # Near head: Bright cyan
                            frame_colors[y_pos][x] = STYLE_CYAN_BRIGHT
                        elif trail_progress < 0.4:
                            # Upper trail: Cyan
                            frame_colors[y_pos][x] = STYLE_CYAN
                        elif trail_progress < 0.7:
                            # Middle trail: Electric Blue
                            frame_colors[y_pos][x] = STYLE_BLUE
                        else:
                            # Tail: Deep Blue (fading)
                            frame_colors[y_pos][x] = STYLE_BLUE_DARK
                
                # Move column down
                col['y'] += col['speed']
                
                # Respawn when off screen
                if head_y - length >= term_height:
                    col['y'] = float(random.randint(-30, -5))
                    col['speed'] = random.uniform(0.8, 2.2)
                    col['length'] = random.randint(8, 25)
                    # Regenerate morphing characters
                    col['chars'] = [random.choice(chars) for _ in range(30)]
            
            # Render frame
            for row_idx, row in enumerate(frame):
                for col_idx, char in enumerate(row):
                    color = frame_colors[row_idx][col_idx]
                    if color:
                        output.append(char, style=f"bold {color}")
                    else:
                        output.append(char)
                output.append("\n")
            
            live.update(output)
            frame_count += 1
            
            # Smooth animation timing
            time.sleep(0.04)





def get_terminal_size() -> tuple:
    """Get current terminal size."""
    size = shutil.get_terminal_size((80, 24))
    return max(size.columns, 60), max(size.lines, 20)


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
        
        # Apply gradient: cyan (top) -> white (middle) -> cyan (bottom)
        if progress < 0.3:
            result.append(centered_line + "\n", style=f"bold {STYLE_BLUE_DARK}")
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
        # Top = Blue
        # Middle = Electric Blue
        # Bottom = Cyan
        if i < total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_BLUE_DARK}")
        elif i < 2 * total_lines / 3:
            result.append(centered + "\n", style=f"bold {STYLE_BLUE}")
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
    result.append("█" * filled, style=f"bold {STYLE_BLUE}")
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
    Enhanced animated splash with Matrix intro.
    
    Sequence:
    1. Matrix rain animation (2 seconds)
    2. Banner + loading bar animation
    3. Program starts
    
    Args:
        skip_animation: If True, shows static version
        duration: Duration of loading animation in seconds (default 5)
    """
    # Clear screen first
    _clear_terminal()
    
    if skip_animation:
        _show_static_splash()
        return
    
    # Phase 1: MATRIX RAIN (2 seconds)
    matrix_rain_animation(duration=2.0)
    
    # Clear for next phase
    _clear_terminal()
    
    # Phase 2: BANNER + LOADING BAR
    # Get terminal size
    term_width, term_height = get_terminal_size()
    
    # Import KR-CLI banner
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Subtitle configuration
    sub_line = "═" * 50
    title_text = "⚡  NO SYSTEM IS SAFE  ⚡"
    desc_text = "Every Firewall Has a Weakness"
    
    # Calculate dimensions for centering
    max_banner_width = max(len(line) for line in kr_lines)
    subtitle_width = len(sub_line)
    max_content_width = max(max_banner_width, subtitle_width)
    
    banner_height = len(kr_lines)
    subtitle_height = 4  # Two separator lines + title + description
    loading_height = 4   # Loading bar section
    total_content_height = banner_height + 1 + subtitle_height + 1 + loading_height
    
    # Vertical centering
    top_padding = max(0, (term_height - total_content_height) // 2)
    
    # Horizontal padding
    banner_padding = max(0, (term_width - max_banner_width) // 2)
    subtitle_padding = max(0, (term_width - subtitle_width) // 2)
    
    # Animated loading
    loading_start = time.time()
    loading_duration = duration - 2.0  # Subtract Matrix time
    
    with Live(console=console, refresh_per_second=30, screen=True) as live:
        while True:
            elapsed = time.time() - loading_start
            if elapsed >= loading_duration:
                break
            
            progress = min(elapsed / loading_duration, 1.0)
            
            output = Text()
            
            # Top padding
            output.append("\n" * top_padding)
            
            # === KR-CLI BANNER (with gradient) ===
            kr_total = len(kr_lines)
            for i, line in enumerate(kr_lines):
                line_progress = i / max(kr_total - 1, 1)
                
                # Blue → Cyan gradient
                if line_progress < 0.33:
                    style = STYLE_BLUE_DARK
                elif line_progress < 0.66:
                    style = STYLE_BLUE
                else:
                    style = STYLE_CYAN
                
                output.append(" " * banner_padding + line + "\n", style=f"bold {style}")
            
            output.append("\n")
            
            # === SUBTITLE SECTION ===
            output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
            
            # Title - properly centered as complete text
            title_padding = max(0, (term_width - len(title_text)) // 2)
            output.append(" " * title_padding + title_text + "\n", style=f"bold {STYLE_CYAN_BRIGHT}")
            
            # Description - centered
            desc_padding = max(0, (term_width - len(desc_text)) // 2)
            output.append(" " * desc_padding + desc_text + "\n", style=f"italic {STYLE_CYAN}")
            
            output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
            output.append("\n")
            
            # === LOADING BAR (Responsive) ===
            bar_width = min(40, term_width - 10)
            bar_padding = max(0, (term_width - bar_width) // 2)
            
            filled = int(bar_width * progress)
            empty = bar_width - filled
            
            output.append(" " * bar_padding)
            output.append("║ ", style=STYLE_CYAN)
            output.append("█" * filled, style=f"bold {STYLE_BLUE}")
            output.append("░" * empty, style=f"dim {STYLE_CYAN}")
            output.append(" ║\n", style=STYLE_CYAN)
            
            # Progress percentage
            pct_text = f"{int(progress * 100)}%"
            pct_padding = max(0, (term_width - len(pct_text)) // 2)
            output.append(" " * pct_padding)
            output.append(pct_text, style=f"bold {STYLE_CYAN}")
            output.append("\n\n")
            
            # Status message (various stages)
            if progress < 0.2:
                status_msg = "⚡ Initializing Systems..."
                status_color = STYLE_BLUE_DARK
            elif progress < 0.4:
                status_msg = "🔐 Loading Security Modules..."
                status_color = STYLE_BLUE
            elif progress < 0.6:
                status_msg = "🤖 Activating AI Engine..."
                status_color = STYLE_CYAN
            elif progress < 0.8:
                status_msg = "🔧 Configuring Tools..."
                status_color = STYLE_BLUE
            else:
                status_msg = "✨ Finalizing Setup..."
                status_color = STYLE_CYAN
            
            status_padding = max(0, (term_width - len(status_msg)) // 2)
            output.append(" " * status_padding)
            output.append(status_msg, style=f"bold {status_color}")
            
            live.update(output)
            time.sleep(0.03)
        
        # Show completion briefly
        output = Text()
        output.append("\n" * top_padding)
        
        # Final banner
        for i, line in enumerate(kr_lines):
            line_progress = i / max(kr_total - 1, 1)
            if line_progress < 0.33:
                style = STYLE_BLUE_DARK
            elif line_progress < 0.66:
                style = STYLE_BLUE
            else:
                style = STYLE_CYAN
            output.append(" " * banner_padding + line + "\n", style=f"bold {style}")
        
        output.append("\n")
        
        # Subtitle with proper centering (same as animation)
        output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
        
        # Title - properly centered
        title_padding = max(0, (term_width - len(title_text)) // 2)
        output.append(" " * title_padding + title_text + "\n", style=f"bold {STYLE_CYAN_BRIGHT}")
        
        # Description - centered
        desc_padding = max(0, (term_width - len(desc_text)) // 2)
        output.append(" " * desc_padding + desc_text + "\n", style=f"italic {STYLE_CYAN}")
        
        output.append(" " * subtitle_padding + sub_line + "\n", style=STYLE_BLUE_DARK)
        output.append("\n")
        
        # Full bar
        output.append(" " * bar_padding)
        output.append("║ ", style=STYLE_CYAN)
        output.append("█" * bar_width, style=f"bold {STYLE_BLUE}")
        output.append(" ║\n", style=STYLE_CYAN)
        
        output.append(" " * ((term_width - 4) // 2))
        output.append("100%\n\n", style=f"bold {STYLE_CYAN}")
        
        output.append(" " * ((term_width - 12) // 2))
        output.append("✅ Ready!\n", style=f"bold {STYLE_CYAN}")
        
        live.update(output)
        time.sleep(0.5)
    
    _clear_terminal()

def _show_static_splash() -> None:
    """Show static splash without animation - fully centered."""
    _clear_terminal()
    
    term_width, term_height = get_terminal_size()
    
    # IMPORT RAW BANNER
    from .display import BANNER_ASCII
    kr_lines = [line for line in BANNER_ASCII.split('\n') if line.strip()]
    
    # Render all elements
    output = Text()
    
    # Calculate vertical centering (only banner + subtitle)
    kr_height = len(kr_lines)
    subtitle_height = 4
    total_height = kr_height + 2 + subtitle_height
    top_padding = max(0, (term_height - total_height) // 2)
    
    output.append("\n" * top_padding)
    
    # KR-CLI (Block centered logic)
    # Calculate banner padding once
    max_kr_width = max(len(line) for line in kr_lines) if kr_lines else 0
    kr_padding = max(0, (term_width - max_kr_width) // 2)

    for i, line in enumerate(kr_lines):
        line_progress = i / max(len(kr_lines) - 1, 1)
        if line_progress < 0.33:
            style = f"bold {STYLE_BLUE_DARK}"
        elif line_progress < 0.66:
            style = f"bold {STYLE_BLUE}"
        else:
            style = f"bold {STYLE_CYAN}"
            
        output.append(" " * kr_padding + line + "\n", style=style)

    output.append("\n")
    
    # ═══════════════════════════════════════════════════════════════════
    # SUBTITLE - Hacker message
    # ═══════════════════════════════════════════════════════════════════
    
    output.append("\n")
    
    # Top separator line
    separator_line = "━" * 60
    sep_padding = max(0, (term_width - len(separator_line)) // 2)
    output.append(" " * sep_padding + separator_line + "\n", style=STYLE_BLUE_DARK)
    
    # Main hacker message
    hacker_msg = "⚡  NO SYSTEM IS SAFE  ⚡"
    msg_padding = max(0, (term_width - len(hacker_msg)) // 2)
    output.append(" " * msg_padding, style="")
    output.append("⚡  ", style=STYLE_CYAN_BRIGHT)
    output.append("NO SYSTEM IS SAFE", style="bold white")
    output.append("  ⚡\n", style=STYLE_CYAN_BRIGHT)
    
    # Description line
    desc_line = "Every Firewall Has a Weakness"
    desc_padding = max(0, (term_width - len(desc_line)) // 2)
    output.append(" " * desc_padding + desc_line + "\n", style=f"italic {STYLE_CYAN}")
    
    # Bottom separator line
    output.append(" " * sep_padding + separator_line, style=STYLE_BLUE_DARK)
    
    console.print(output)
    console.print()


# ═══════════════════════════════════════════════════════════════════════════════
# THEME UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_style_red() -> str:
    return STYLE_BLUE_DARK

def get_style_orange() -> str:
    return STYLE_BLUE

def get_style_cyan() -> str:
    return STYLE_CYAN

def get_style_pink() -> str:
    return STYLE_PINK


# Test
if __name__ == "__main__":
    animated_splash(duration=5.0)

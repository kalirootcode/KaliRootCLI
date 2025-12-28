"""
Terminal colors and styling for KaliRoot CLI
Professional Blue/Cyan Hacker Theme (Matrix Style)
"""


class Colors:
    """ANSI color codes for terminal styling."""
    
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    
    # Bold colors
    BOLD_BLACK = '\033[1;30m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_PURPLE = '\033[1;35m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def success(cls, text: str) -> str:
        """Green success text."""
        return cls.colorize(text, cls.GREEN)
    
    @classmethod
    def error(cls, text: str) -> str:
        """Red error text."""
        return cls.colorize(text, cls.RED)
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow warning text."""
        return cls.colorize(text, cls.YELLOW)
    
    @classmethod
    def info(cls, text: str) -> str:
        """Cyan info text."""
        return cls.colorize(text, cls.CYAN)
    
    @classmethod
    def highlight(cls, text: str) -> str:
        """Bold white highlighted text."""
        return cls.colorize(text, cls.BOLD_WHITE)


# ═══════════════════════════════════════════════════════════════════════════════
# HACKER BLUE/CYAN THEME - Matrix/Cyberpunk Style
# ═══════════════════════════════════════════════════════════════════════════════

# Core palette
STYLE_BG_DEEP = "rgb(0,0,0)"              # Pure black background
STYLE_TEXT = "rgb(255,255,255)"           # Pure white text
STYLE_TEXT_DIM = "rgb(120,120,120)"       # Dimmed gray

# Primary accents (Blue spectrum - Matrix style)
STYLE_BLUE_DARK = "rgb(0,50,150)"         # Dark blue - deep accents
STYLE_BLUE = "rgb(0,100,255)"             # Electric blue - main accent
STYLE_BLUE_BRIGHT = "rgb(100,150,255)"    # Bright blue - highlights

# Secondary accents (Cyan/Aqua - Hacker green-blue)
STYLE_CYAN_DARK = "rgb(0,150,150)"        # Dark cyan
STYLE_CYAN = "rgb(0,255,255)"             # Electric cyan/aqua
STYLE_CYAN_BRIGHT = "rgb(100,255,255)"    # Bright cyan
STYLE_MATRIX_GREEN = "rgb(0,255,65)"      # Matrix green accent

# Status colors
STYLE_SUCCESS = "rgb(0,255,65)"           # Matrix green
STYLE_WARNING = "rgb(255,200,0)"          # Amber
STYLE_ERROR = "rgb(255,50,50)"            # Red

# Rainbow gradient (lolcat-style effect for banners)
GRADIENT_BLUE_CYAN = [
    "rgb(0,50,200)",       # Deep Blue
    "rgb(0,100,255)",      # Blue
    "rgb(0,150,255)",      # Light Blue
    "rgb(0,200,255)",      # Sky Blue
    "rgb(0,255,200)",      # Cyan-Green
    "rgb(0,255,255)",      # Cyan
]

# Theme dictionary (Blue/Cyan hacker aesthetic)
THEME = {
    # Backgrounds
    "bg": STYLE_BG_DEEP,
    
    # Text
    "text": STYLE_TEXT,
    "text_dim": STYLE_TEXT_DIM,
    
    # Primary accents
    "primary": STYLE_BLUE,
    "primary_light": STYLE_BLUE_BRIGHT,
    "header": STYLE_BLUE_DARK,
    
    # Secondary accents
    "secondary": STYLE_CYAN,
    "border": STYLE_CYAN,
    "accent": STYLE_CYAN_BRIGHT,
    
    # Status
    "success": STYLE_SUCCESS,
    "error": STYLE_ERROR,
    "warning": STYLE_WARNING,
    "info": STYLE_CYAN,
    
    # UI elements
    "menu_number": STYLE_BLUE,
    "menu_item": STYLE_TEXT,
    "menu_desc": STYLE_TEXT_DIM,
    "divider": STYLE_CYAN_DARK,
    
    # Legacy compatibility
    "muted": STYLE_TEXT_DIM,
}

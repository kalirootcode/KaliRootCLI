"""
Terminal colors and styling for KaliRoot CLI
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


# Theme colors for the app
THEME = {
    "primary": "cyan",
    "secondary": "yellow",
    "success": "green",
    "error": "red",
    "warning": "yellow",
    "info": "blue",
    "muted": "dim white",
    "accent": "magenta",
    "header": "bold cyan",
    "menu_item": "white",
    "menu_number": "cyan",
}

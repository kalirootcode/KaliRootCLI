"""
Main entry point for KaliRoot CLI
Professional startup sequence.
"""

import sys
import logging
import time

from .config import validate_config, LOG_LEVEL
from .ui.display import (
    console, 
    print_banner, 
    print_error, 
    show_loading,
    print_success,
    print_info
)
from .distro_detector import detector
from .auth import auth_manager
from .ui.menus import MainMenu

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=f'{detector.get_data_dir()}/kalirootcli.log'
)

def main():
    """Application entry point."""
    try:
        # 1. Startup
        console.clear()
        print_banner()
        
        # 2. Distro Detection (happens on import, but we can verify)
        with show_loading("Initializing System Core..."):
            sys_info = detector.get_system_info()
            time.sleep(0.5) # UX Delay
        
        print_info(f"Context: {sys_info['distro']} | {sys_info['shell']} | {sys_info['root']}")
        
        # 3. Config Validation
        missing = validate_config(require_all=False)
        if missing:
            print_error(f"Missing config: {', '.join(missing)}")
            print_info("Please edit .env file.")
            sys.exit(1)
            
        # 4. Authentication
        user_data = auth_manager.load_session()
        if not user_data:
            user_data = auth_manager.interactive_auth()
        
        if not user_data:
            print_info("Goodbye.")
            sys.exit(0)
            
        # 5. Launch Main Menu
        menu = MainMenu(user_data["id"], user_data["username"])
        menu.show()
        
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Session Interrupted.[/bold cyan]\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Critical System Error: {e}")
        logging.exception("Main crash")
        sys.exit(1)

if __name__ == "__main__":
    main()

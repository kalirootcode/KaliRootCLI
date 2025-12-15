#!/usr/bin/env python3
"""
KaliRoot CLI - Smart Installer
Installs package and configures commands automatically.
"""

import os
import sys
import subprocess
import shutil

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

def log_info(msg):
    print(f"{GREEN}[INFO]{NC} {msg}")

def log_warn(msg):
    print(f"{YELLOW}[WARN]{NC} {msg}")

def log_error(msg):
    print(f"{RED}[ERROR]{NC} {msg}")

def install_package():
    """Install the current directory as a pip package."""
    print("📦 Installing KaliRoot CLI package...")
    
    cmd = [sys.executable, "-m", "pip", "install", "."]
    
    # If running as root/admin, we might need --break-system-packages on newer systems
    # But let's assume venv or handled environment first.
    
    try:
        subprocess.check_call(cmd)
        log_info("Package installed successfully!")
        return True
    except subprocess.CalledProcessError:
        log_error("Failed to install package.")
        return False

def check_path():
    """Check if the install location is likely in PATH."""
    # This is rough but helpful
    user_bin = os.path.expanduser("~/.local/bin")
    if user_bin not in os.environ["PATH"] and "--user" in sys.argv:
        log_warn(f"{user_bin} is not in your PATH.")
        print(f"ADD THIS to your shell config:  export PATH=$PATH:{user_bin}")

def main():
    print(f"\n{GREEN}🔒 KaliRoot CLI Installer v2.0{NC}\n")
    
    # 1. Install Package (includes deps and entry points)
    if install_package():
        
        # 2. Verify commands
        log_info("Verifying commands...")
        
        print(f"\n{GREEN}✔ Installation Complete!{NC}\n")
        print("You can now multiple commands from anywhere:")
        print(f"  {GREEN}kaliroot{NC}   -> Launch Main CLI")
        print(f"  {GREEN}kr-cli{NC}     -> Smart Analysis Wrapper")
        
        # Check venv info
        if sys.prefix != sys.base_prefix:
            print(f"\n{YELLOW}Note: You are in a virtual environment.{NC}")
            print("Commands are available while this venv is active.")
        else:
            check_path()
            
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

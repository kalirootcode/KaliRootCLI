#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        KR-CLI DOMINION - Professional Installer               ║
║                      Compatible with Linux distros & Termux                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

This installer:
  1. Shows animated RK-CLI SETUP intro
  2. Displays Terms & Conditions (accept/decline)
  3. Detects environment (Linux distro or Termux)
  4. Creates a clean virtual environment
  5. Installs kr-cli-dominion from PyPI with live progress
  6. Activates venv and launches kr-clidn

Requirements: Python 3.8+ (will install Rich inside venv)
Usage: python3 setup_kr_cli.py
"""

import os
import sys
import time
import shutil
import subprocess
import platform
import threading
import re
from pathlib import Path
from collections import deque

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

VERSION = "1.1.0"
INSTALL_DIR = Path.home() / ".kr-cli-dominion"
VENV_DIR = INSTALL_DIR / "venv"
PACKAGE_NAME = "kr-cli-dominion"

# ANSI Colors (for pre-Rich display)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

# Terms and Conditions
TERMS_AND_CONDITIONS = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         TÉRMINOS Y CONDICIONES                               ║
║                           KR-CLI DOMINION v5.7                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

                              LICENCIA MIT

Copyright (c) 2024-2026 KaliRootCode

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una 
copia de este software y los archivos de documentación asociados (el "Software"),
para tratar el Software sin restricciones, incluyendo sin limitación los 
derechos de usar, copiar, modificar, fusionar, publicar, distribuir, 
sublicenciar y/o vender copias del Software.

                         TÉRMINOS DE USO

1. USO ÉTICO Y LEGAL
   - KR-CLI Dominion está diseñado para profesionales de ciberseguridad
   - Solo debe usarse en sistemas donde tenga autorización explícita
   - El uso indebido para actividades ilegales está prohibido
   - El usuario asume toda responsabilidad por el uso de la herramienta

2. ANÁLISIS CON IA
   - Los comandos son analizados por modelos de IA (Groq/Gemini)
   - Los datos de comandos pueden ser procesados en servidores externos
   - No ingrese información confidencial o sensible
   - Los reportes generados son orientativos, no garantizamos precisión

3. CONECTIVIDAD
   - Requiere conexión a Internet para funciones de IA
   - Se conecta a servidores de API para autenticación y análisis
   - Los créditos de uso son gestionados remotamente

4. SIN GARANTÍA
   - El software se proporciona "TAL CUAL", sin garantías de ningún tipo
   - Los autores no serán responsables de daños derivados del uso

5. PRIVACIDAD
   - Se recopilan datos básicos de uso para mejorar el servicio
   - No se vende ni comparte información personal a terceros
   - Los datos de sesión son cifrados y protegidos

══════════════════════════════════════════════════════════════════════════════

Al aceptar, confirma que ha leído y acepta estos términos.
"""

# ASCII Art Logo
LOGO_FRAMES = [
    r"""
    ██████╗ ██╗  ██╗       ██████╗██╗     ██╗
    ██╔══██╗██║ ██╔╝      ██╔════╝██║     ██║
    ██████╔╝█████╔╝ █████╗██║     ██║     ██║
    ██╔══██╗██╔═██╗ ╚════╝██║     ██║     ██║
    ██║  ██║██║  ██╗      ╚██████╗███████╗██║
    ╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
    """,
]

SETUP_BANNER = r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     ███████╗███████╗████████╗██╗   ██╗██████╗                ║
    ║     ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗               ║
    ║     ███████╗█████╗     ██║   ██║   ██║██████╔╝               ║
    ║     ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝                ║
    ║     ███████║███████╗   ██║   ╚██████╔╝██║                    ║
    ║     ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝                    ║
    ║                                                               ║
    ║            Professional Installer v{version}                      ║
    ╚═══════════════════════════════════════════════════════════════╝
"""


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color=Colors.RESET, end="\n"):
    """Print colored text."""
    print(f"{color}{text}{Colors.RESET}", end=end)

def get_terminal_width():
    """Get terminal width."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def run_command(cmd, capture=True, check=False, env=None):
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=capture,
            text=True,
            check=check,
            env=env or os.environ.copy()
        )
        return result
    except subprocess.CalledProcessError as e:
        return e
    except Exception as e:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# ANIMATED PROGRESS BAR
# ══════════════════════════════════════════════════════════════════════════════

class AnimatedProgressBar:
    """Animated progress bar with real pip output."""
    
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    BAR_CHARS = "█▓▒░"
    
    def __init__(self, title="Installing"):
        self.title = title
        self.current_package = ""
        self.packages_installed = []
        self.log_lines = deque(maxlen=5)
        self.spinner_idx = 0
        self.progress = 0
        self.total_packages = 0
        self.running = False
        self.start_time = None
        
    def start(self):
        """Start the progress display."""
        self.running = True
        self.start_time = time.time()
        self._print_header()
        
    def _print_header(self):
        """Print the installation header."""
        print()
        print(f"    {Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"    {Colors.BRIGHT_CYAN}║{Colors.RESET}          {Colors.BOLD}🚀 INSTALANDO KR-CLI DOMINION{Colors.RESET}                     {Colors.BRIGHT_CYAN}║{Colors.RESET}")
        print(f"    {Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
    
    def update(self, line):
        """Update progress with a pip output line."""
        line = line.strip()
        if not line:
            return
            
        self.log_lines.append(line)
        
        # Parse pip output
        if "Collecting" in line:
            pkg = line.replace("Collecting", "").strip().split()[0]
            self.current_package = pkg
            self.total_packages += 1
        elif "Downloading" in line:
            # Extract package and size
            match = re.search(r'Downloading\s+(\S+)', line)
            if match:
                self.current_package = f"⬇ {match.group(1).split('/')[-1][:40]}"
        elif "Installing collected packages" in line:
            self.current_package = "📦 Finalizando instalación..."
        elif "Successfully installed" in line:
            # Parse installed packages
            pkgs = line.replace("Successfully installed", "").strip().split()
            self.packages_installed = pkgs
            self.current_package = f"✓ {len(pkgs)} paquetes instalados"
        
        self._render()
    
    def _render(self):
        """Render the current progress state."""
        term_width = min(get_terminal_width(), 80)
        
        # Spinner
        spinner = self.SPINNER_FRAMES[self.spinner_idx % len(self.SPINNER_FRAMES)]
        self.spinner_idx += 1
        
        # Time elapsed
        elapsed = time.time() - self.start_time if self.start_time else 0
        time_str = f"{int(elapsed)}s"
        
        # Progress bar (indeterminate)
        bar_width = 30
        pos = int((elapsed * 2) % bar_width)
        bar = ""
        for i in range(bar_width):
            if i >= pos - 3 and i <= pos + 3:
                intensity = 3 - abs(i - pos)
                bar += self.BAR_CHARS[max(0, min(3, intensity))]
            else:
                bar += "░"
        
        # Current status line
        status = self.current_package[:50] if self.current_package else "Conectando..."
        
        # Build output
        print(f"\r    {Colors.BRIGHT_CYAN}{spinner}{Colors.RESET} ", end="")
        print(f"{Colors.BRIGHT_GREEN}{bar}{Colors.RESET} ", end="")
        print(f"{Colors.DIM}[{time_str}]{Colors.RESET} ", end="")
        print(f"{Colors.BRIGHT_WHITE}{status:<50}{Colors.RESET}", end="", flush=True)
    
    def add_log_line(self, line):
        """Add a log line to display."""
        self.log_lines.append(line)
        
    def finish(self, success=True):
        """Finish the progress display."""
        self.running = False
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        print()
        print()
        
        if success:
            print(f"    {Colors.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"    {Colors.BRIGHT_GREEN}║{Colors.RESET}               {Colors.BOLD}✅ INSTALACIÓN COMPLETADA{Colors.RESET}                    {Colors.BRIGHT_GREEN}║{Colors.RESET}")
            print(f"    {Colors.BRIGHT_GREEN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
            print()
            print(f"    {Colors.DIM}Tiempo total: {elapsed:.1f} segundos{Colors.RESET}")
            print(f"    {Colors.DIM}Paquetes instalados: {len(self.packages_installed)}{Colors.RESET}")
        else:
            print(f"    {Colors.BRIGHT_RED}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"    {Colors.BRIGHT_RED}║{Colors.RESET}               {Colors.BOLD}❌ ERROR EN INSTALACIÓN{Colors.RESET}                      {Colors.BRIGHT_RED}║{Colors.RESET}")
            print(f"    {Colors.BRIGHT_RED}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")


class LivePipInstaller:
    """Run pip install with live output and animated progress."""
    
    def __init__(self, pip_path: Path, package: str):
        self.pip_path = pip_path
        self.package = package
        self.success = False
        self.output_lines = []
        self.error_output = ""
        
    def install(self):
        """Run installation with live progress."""
        progress = AnimatedProgressBar()
        progress.start()
        
        try:
            # Run pip with unbuffered output
            process = subprocess.Popen(
                [str(self.pip_path), "install", "--progress-bar", "off", self.package],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.output_lines.append(line.strip())
                    progress.update(line)
            
            # Get return code
            return_code = process.wait()
            self.success = return_code == 0
            
            if not self.success:
                self.error_output = "\n".join(self.output_lines[-10:])
            
        except Exception as e:
            self.success = False
            self.error_output = str(e)
        
        progress.finish(self.success)
        return self.success


# ══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT DETECTOR
# ══════════════════════════════════════════════════════════════════════════════

class EnvironmentDetector:
    """Detect system environment and available tools."""
    
    def __init__(self):
        self.os_name = None
        self.os_version = None
        self.is_termux = False
        self.python_cmd = None
        self.pip_cmd = None
        self.pkg_manager = None
        self.pkg_install_cmd = None
        self.venv_available = False
        self.shell = None
        self.shell_rc = None
        
    def detect_all(self):
        """Run all detection methods."""
        self._detect_os()
        self._detect_python()
        self._detect_pip()
        self._detect_package_manager()
        self._detect_venv()
        self._detect_shell()
        return self
    
    def _detect_os(self):
        """Detect operating system and distribution."""
        # Check for Termux first
        if os.path.exists("/data/data/com.termux"):
            self.os_name = "Termux"
            self.os_version = "Android"
            self.is_termux = True
            return
        
        # Check /etc/os-release for Linux distros
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                
            if "kali" in content:
                self.os_name = "Kali Linux"
            elif "ubuntu" in content:
                self.os_name = "Ubuntu"
            elif "debian" in content:
                self.os_name = "Debian"
            elif "fedora" in content:
                self.os_name = "Fedora"
            elif "centos" in content or "rhel" in content or "red hat" in content:
                self.os_name = "RHEL/CentOS"
            elif "arch" in content:
                self.os_name = "Arch Linux"
            elif "manjaro" in content:
                self.os_name = "Manjaro"
            elif "opensuse" in content or "suse" in content:
                self.os_name = "openSUSE"
            elif "alpine" in content:
                self.os_name = "Alpine"
            else:
                self.os_name = "Linux"
                
            # Get version
            for line in open("/etc/os-release"):
                if line.startswith("VERSION_ID="):
                    self.os_version = line.split("=")[1].strip().strip('"')
                    break
        else:
            self.os_name = platform.system()
            self.os_version = platform.release()
    
    def _detect_python(self):
        """Find available Python command."""
        for cmd in ["python3", "python"]:
            result = run_command([cmd, "--version"])
            if result and result.returncode == 0:
                version = result.stdout.strip() if result.stdout else result.stderr.strip()
                # Check version >= 3.8
                if "3." in version:
                    try:
                        minor = int(version.split(".")[1].split()[0])
                        if minor >= 8:
                            self.python_cmd = cmd
                            return
                    except:
                        pass
    
    def _detect_pip(self):
        """Find available pip command."""
        for cmd in ["pip3", "pip"]:
            result = run_command([cmd, "--version"])
            if result and result.returncode == 0:
                self.pip_cmd = cmd
                return
        
        # Try python -m pip
        if self.python_cmd:
            result = run_command([self.python_cmd, "-m", "pip", "--version"])
            if result and result.returncode == 0:
                self.pip_cmd = f"{self.python_cmd} -m pip"
    
    def _detect_package_manager(self):
        """Detect system package manager."""
        managers = {
            "apt": "apt install -y",
            "apt-get": "apt-get install -y", 
            "dnf": "dnf install -y",
            "yum": "yum install -y",
            "pacman": "pacman -S --noconfirm",
            "zypper": "zypper install -y",
            "apk": "apk add",
            "pkg": "pkg install -y",  # Termux
        }
        
        for mgr, install_cmd in managers.items():
            if shutil.which(mgr):
                self.pkg_manager = mgr
                self.pkg_install_cmd = install_cmd
                return
    
    def _detect_venv(self):
        """Check if venv module is available."""
        if self.python_cmd:
            result = run_command([self.python_cmd, "-m", "venv", "--help"])
            self.venv_available = result and result.returncode == 0
    
    def _detect_shell(self):
        """Detect user's shell and rc file."""
        shell = os.environ.get("SHELL", "/bin/bash")
        self.shell = os.path.basename(shell)
        
        # Determine rc file
        home = Path.home()
        if self.shell == "zsh":
            self.shell_rc = home / ".zshrc"
        elif self.shell == "fish":
            self.shell_rc = home / ".config" / "fish" / "config.fish"
        else:
            self.shell_rc = home / ".bashrc"
    
    def get_venv_activate_command(self, venv_path: Path):
        """Get the command to activate venv based on shell."""
        if self.is_termux or os.name != 'nt':
            activate_script = venv_path / "bin" / "activate"
        else:
            activate_script = venv_path / "Scripts" / "activate"
        
        if self.shell == "fish":
            return f"source {activate_script}.fish"
        else:
            return f"source {activate_script}"
    
    def get_summary(self):
        """Return a summary dict of detected environment."""
        return {
            "os": self.os_name,
            "version": self.os_version,
            "is_termux": self.is_termux,
            "python": self.python_cmd,
            "pip": self.pip_cmd,
            "pkg_manager": self.pkg_manager,
            "venv_available": self.venv_available,
            "shell": self.shell,
            "shell_rc": str(self.shell_rc) if self.shell_rc else None
        }


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PREPARATOR
# ══════════════════════════════════════════════════════════════════════════════

class SystemPreparator:
    """Prepare system with required dependencies."""
    
    def __init__(self, env: EnvironmentDetector):
        self.env = env
        self.errors = []
    
    def install_venv_package(self):
        """Install python venv package if missing."""
        if self.env.venv_available:
            return True
        
        if not self.env.pkg_manager:
            self.errors.append("No package manager found to install python3-venv")
            return False
        
        # Package names vary by distro
        venv_packages = {
            "apt": "python3-venv",
            "apt-get": "python3-venv",
            "dnf": "python3-virtualenv",
            "yum": "python3-virtualenv",
            "pacman": "python-virtualenv",
            "zypper": "python3-virtualenv",
            "apk": "py3-virtualenv",
            "pkg": "python",  # Termux includes venv with python
        }
        
        pkg = venv_packages.get(self.env.pkg_manager, "python3-venv")
        cmd = f"sudo {self.env.pkg_install_cmd} {pkg}" if not self.env.is_termux else f"{self.env.pkg_install_cmd} {pkg}"
        
        result = run_command(cmd)
        if result and result.returncode == 0:
            self.env._detect_venv()  # Re-check
            return self.env.venv_available
        
        self.errors.append(f"Failed to install {pkg}")
        return False
    
    def install_termux_deps(self):
        """Install Termux-specific dependencies."""
        if not self.env.is_termux:
            return True
        
        packages = ["python", "clang", "make", "pkg-config", "libxml2", "libxslt", "openssl"]
        cmd = f"pkg install -y {' '.join(packages)}"
        
        result = run_command(cmd)
        return result and result.returncode == 0


# ══════════════════════════════════════════════════════════════════════════════
# VIRTUAL ENVIRONMENT MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class VirtualEnvManager:
    """Manage Python virtual environment."""
    
    def __init__(self, env: EnvironmentDetector, venv_path: Path):
        self.env = env
        self.venv_path = venv_path
        self.venv_python = None
        self.venv_pip = None
        
    def create_venv(self):
        """Create a new virtual environment."""
        # Remove existing if present
        if self.venv_path.exists():
            shutil.rmtree(self.venv_path)
        
        # Create parent directory
        self.venv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create venv
        result = run_command([self.env.python_cmd, "-m", "venv", str(self.venv_path)])
        if not result or result.returncode != 0:
            return False
        
        # Set paths
        if self.env.is_termux or os.name != 'nt':
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"
        else:
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
        
        return self.venv_python.exists()
    
    def upgrade_pip(self):
        """Upgrade pip in venv."""
        result = run_command([str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip", "-q"])
        return result and result.returncode == 0
    
    def install_package(self, package_name):
        """Install a package in the venv with live progress."""
        installer = LivePipInstaller(self.venv_pip, package_name)
        return installer.install()
    
    def get_bin_path(self):
        """Get the bin directory path."""
        if self.env.is_termux or os.name != 'nt':
            return self.venv_path / "bin"
        return self.venv_path / "Scripts"
    
    def get_activate_command(self):
        """Get the activate command for the current shell."""
        return self.env.get_venv_activate_command(self.venv_path)


# ══════════════════════════════════════════════════════════════════════════════
# INSTALLER UI (Pre-Rich - ANSI based)
# ══════════════════════════════════════════════════════════════════════════════

class InstallerUI:
    """Handle installer UI before Rich is available."""
    
    @staticmethod
    def show_intro_animation():
        """Show animated intro screen."""
        clear_screen()
        
        # Color gradient for animation
        colors = [
            Colors.BRIGHT_BLUE,
            Colors.BRIGHT_CYAN, 
            Colors.BRIGHT_MAGENTA,
            Colors.BRIGHT_RED,
            Colors.BRIGHT_YELLOW,
            Colors.BRIGHT_GREEN,
        ]
        
        # Animate logo appearance
        logo_lines = LOGO_FRAMES[0].split("\n")
        
        for i, line in enumerate(logo_lines):
            color = colors[i % len(colors)]
            print(f"{color}{line}{Colors.RESET}")
            time.sleep(0.08)
        
        time.sleep(0.5)
        
        # Show SETUP banner with animation
        clear_screen()
        
        setup_text = SETUP_BANNER.format(version=VERSION)
        for line in setup_text.split("\n"):
            print(f"{Colors.BRIGHT_CYAN}{line}{Colors.RESET}")
            time.sleep(0.03)
        
        time.sleep(1)
        
        # Loading animation
        print()
        loading_chars = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"
        print(f"    {Colors.DIM}Initializing", end="", flush=True)
        for _ in range(2):
            for char in loading_chars:
                print(f"\r    {Colors.BRIGHT_CYAN}Initializing {char * 10}{Colors.RESET}", end="", flush=True)
                time.sleep(0.05)
        print(f"\r    {Colors.BRIGHT_GREEN}✓ Ready{' ' * 20}{Colors.RESET}")
        time.sleep(0.5)
    
    @staticmethod
    def show_terms():
        """Show terms and conditions, return True if accepted."""
        clear_screen()
        
        print(f"{Colors.BRIGHT_CYAN}{TERMS_AND_CONDITIONS}{Colors.RESET}")
        
        print()
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}┌─────────────────────────────────────┐{Colors.RESET}")
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}│  {Colors.BRIGHT_GREEN}[A]{Colors.BRIGHT_WHITE} Aceptar   {Colors.BRIGHT_RED}[S]{Colors.BRIGHT_WHITE} Salir          │{Colors.RESET}")
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}└─────────────────────────────────────┘{Colors.RESET}")
        print()
        
        while True:
            try:
                choice = input(f"    {Colors.BRIGHT_YELLOW}➤ Su elección: {Colors.RESET}").strip().lower()
                if choice in ['a', 'aceptar', 'accept', 'y', 'yes', 'si', 'sí']:
                    return True
                elif choice in ['s', 'salir', 'exit', 'n', 'no', 'q', 'quit']:
                    return False
                else:
                    print(f"    {Colors.RED}Por favor ingrese [A] para aceptar o [S] para salir{Colors.RESET}")
            except KeyboardInterrupt:
                return False
    
    @staticmethod
    def show_environment_info(env: EnvironmentDetector):
        """Display detected environment information."""
        clear_screen()
        
        print(f"\n{Colors.BRIGHT_CYAN}    ╔══════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}    ║          🔍 ANÁLISIS DEL SISTEMA                    ║{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}    ╚══════════════════════════════════════════════════════╝{Colors.RESET}\n")
        
        items = [
            ("Sistema Operativo", env.os_name or "Unknown", Colors.BRIGHT_WHITE),
            ("Versión", env.os_version or "Unknown", Colors.BRIGHT_WHITE),
            ("Es Termux", "Sí" if env.is_termux else "No", Colors.BRIGHT_YELLOW if env.is_termux else Colors.DIM),
            ("Python", env.python_cmd or "❌ No encontrado", Colors.BRIGHT_GREEN if env.python_cmd else Colors.BRIGHT_RED),
            ("Pip", env.pip_cmd or "❌ No encontrado", Colors.BRIGHT_GREEN if env.pip_cmd else Colors.BRIGHT_RED),
            ("Gestor de paquetes", env.pkg_manager or "No detectado", Colors.BRIGHT_BLUE if env.pkg_manager else Colors.DIM),
            ("Venv disponible", "✓ Sí" if env.venv_available else "❌ No", Colors.BRIGHT_GREEN if env.venv_available else Colors.BRIGHT_RED),
            ("Shell", env.shell or "Unknown", Colors.BRIGHT_WHITE),
        ]
        
        for label, value, color in items:
            print(f"    {Colors.BRIGHT_WHITE}{label:.<25}{Colors.RESET} {color}{value}{Colors.RESET}")
            time.sleep(0.15)
        
        print()
        time.sleep(0.5)
    
    @staticmethod
    def show_step(step_name, icon="📦"):
        """Show a step indicator."""
        print(f"\n    {Colors.BRIGHT_CYAN}{icon} {step_name}...{Colors.RESET}")
    
    @staticmethod
    def show_step_done(message="Completado"):
        """Show step completion."""
        print(f"    {Colors.BRIGHT_GREEN}✓ {message}{Colors.RESET}")
    
    @staticmethod
    def show_error(message):
        """Show error message."""
        print(f"\n    {Colors.BRIGHT_RED}╔══════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"    {Colors.BRIGHT_RED}║                    ❌ ERROR                          ║{Colors.RESET}")
        print(f"    {Colors.BRIGHT_RED}╚══════════════════════════════════════════════════════╝{Colors.RESET}")
        print(f"\n    {Colors.RED}{message}{Colors.RESET}\n")
    
    @staticmethod
    def show_final_success(install_dir: Path, venv_manager: VirtualEnvManager, env: EnvironmentDetector):
        """Show final success message with launch instructions."""
        venv_path = venv_manager.venv_path
        
        print()
        print(f"    {Colors.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"    {Colors.BRIGHT_GREEN}║          🎉 KR-CLI DOMINION INSTALADO EXITOSAMENTE          ║{Colors.RESET}")
        print(f"    {Colors.BRIGHT_GREEN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}📍 Carpeta de instalación:{Colors.RESET}")
        print(f"       {Colors.BRIGHT_CYAN}{install_dir}{Colors.RESET}")
        print()
        
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}� Entorno virtual:{Colors.RESET}")
        print(f"       {Colors.DIM}{venv_path}{Colors.RESET}")
        print()
        
        # Main usage instructions - CLEAR STEP BY STEP
        print(f"    {Colors.BRIGHT_YELLOW}{'═' * 60}{Colors.RESET}")
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}📋 CÓMO EJECUTAR KR-CLI DOMINION:{Colors.RESET}")
        print(f"    {Colors.BRIGHT_YELLOW}{'═' * 60}{Colors.RESET}")
        print()
        
        print(f"    {Colors.BRIGHT_GREEN}Paso 1:{Colors.RESET} Ir a la carpeta de instalación")
        print(f"           {Colors.BOLD}{Colors.BRIGHT_WHITE}cd {install_dir}{Colors.RESET}")
        print()
        
        print(f"    {Colors.BRIGHT_GREEN}Paso 2:{Colors.RESET} Activar el entorno virtual")
        print(f"           {Colors.BOLD}{Colors.BRIGHT_WHITE}source venv/bin/activate{Colors.RESET}")
        print()
        
        print(f"    {Colors.BRIGHT_GREEN}Paso 3:{Colors.RESET} Ejecutar el programa")
        print(f"           {Colors.BOLD}{Colors.BRIGHT_WHITE}kr-clidn{Colors.RESET}")
        print()
        
        print(f"    {Colors.BRIGHT_YELLOW}{'═' * 60}{Colors.RESET}")
        print()
        
        # Quick one-liner
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}⚡ Comando rápido (una sola línea):{Colors.RESET}")
        print(f"       {Colors.DIM}cd {install_dir} && source venv/bin/activate && kr-clidn{Colors.RESET}")
        print()
        
        # Optional: Create alias
        print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}💡 TIP: Crear alias permanente{Colors.RESET}")
        print(f"       Añade esto a tu {Colors.CYAN}{env.shell_rc}{Colors.RESET}:")
        print(f"       {Colors.DIM}alias kr='cd {install_dir} && source venv/bin/activate && kr-clidn'{Colors.RESET}")
        print()
    
    @staticmethod
    def ask_launch(install_dir: Path):
        """Ask if user wants to launch kr-clidn."""
        print(f"    {Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"    {Colors.BRIGHT_CYAN}║      ¿Deseas iniciar KR-CLI DOMINION ahora? [S/n]           ║{Colors.RESET}")
        print(f"    {Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        print(f"    {Colors.DIM}Se ejecutarán los siguientes comandos:{Colors.RESET}")
        print(f"    {Colors.DIM}  1. cd {install_dir}{Colors.RESET}")
        print(f"    {Colors.DIM}  2. source venv/bin/activate{Colors.RESET}")
        print(f"    {Colors.DIM}  3. kr-clidn{Colors.RESET}")
        print()
        
        try:
            choice = input(f"    {Colors.BRIGHT_YELLOW}➤ {Colors.RESET}").strip().lower()
            return choice not in ['n', 'no']
        except KeyboardInterrupt:
            return False


# ══════════════════════════════════════════════════════════════════════════════
# LAUNCH KR-CLIDN
# ══════════════════════════════════════════════════════════════════════════════

def launch_kr_clidn(install_dir: Path, venv_manager: VirtualEnvManager, env: EnvironmentDetector):
    """Launch kr-clidn with the virtual environment activated."""
    bin_path = venv_manager.get_bin_path()
    kr_clidn_path = bin_path / "kr-clidn"
    venv_path = venv_manager.venv_path
    
    if not kr_clidn_path.exists():
        print(f"    {Colors.RED}❌ Error: kr-clidn no encontrado en {kr_clidn_path}{Colors.RESET}")
        return False
    
    print()
    print(f"    {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
    print(f"    {Colors.BOLD}{Colors.BRIGHT_WHITE}🚀 EJECUTANDO KR-CLI DOMINION{Colors.RESET}")
    print(f"    {Colors.BRIGHT_CYAN}{'═' * 60}{Colors.RESET}")
    print()
    
    # Show what we're doing
    print(f"    {Colors.BRIGHT_GREEN}➤{Colors.RESET} cd {Colors.BRIGHT_WHITE}{install_dir}{Colors.RESET}")
    time.sleep(0.3)
    os.chdir(install_dir)
    
    print(f"    {Colors.BRIGHT_GREEN}➤{Colors.RESET} source {Colors.BRIGHT_WHITE}venv/bin/activate{Colors.RESET}")
    time.sleep(0.3)
    
    print(f"    {Colors.BRIGHT_GREEN}➤{Colors.RESET} {Colors.BRIGHT_WHITE}kr-clidn{Colors.RESET}")
    time.sleep(0.5)
    
    print()
    print(f"    {Colors.DIM}─────────────────────────────────────────{Colors.RESET}")
    print()
    time.sleep(0.5)
    
    # Create environment with venv activated
    venv_env = os.environ.copy()
    venv_env["VIRTUAL_ENV"] = str(venv_path)
    venv_env["PATH"] = f"{bin_path}:{venv_env.get('PATH', '')}"
    
    # Remove PYTHONHOME if set
    if "PYTHONHOME" in venv_env:
        del venv_env["PYTHONHOME"]
    
    try:
        # Execute kr-clidn, replacing current process
        os.execve(str(kr_clidn_path), [str(kr_clidn_path)], venv_env)
    except Exception as e:
        # Fallback: run as subprocess
        try:
            subprocess.run([str(kr_clidn_path)], env=venv_env, cwd=str(install_dir))
        except Exception as e2:
            print(f"    {Colors.RED}Error al iniciar: {e2}{Colors.RESET}")
            return False
    
    return True


# ══════════════════════════════════════════════════════════════════════════════
# MAIN INSTALLER FLOW
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Main installer entry point."""
    try:
        # 1. Show intro animation
        InstallerUI.show_intro_animation()
        
        # 2. Show terms and conditions
        if not InstallerUI.show_terms():
            print(f"\n    {Colors.YELLOW}👋 Instalación cancelada. ¡Hasta pronto!{Colors.RESET}\n")
            return 0
        
        # 3. Detect environment
        print(f"\n    {Colors.BRIGHT_CYAN}🔍 Analizando sistema...{Colors.RESET}")
        env = EnvironmentDetector().detect_all()
        time.sleep(0.5)
        
        InstallerUI.show_environment_info(env)
        
        # 4. Check Python availability
        if not env.python_cmd:
            InstallerUI.show_error(
                "Python 3.8+ no encontrado.\n\n"
                "Por favor instala Python primero:\n"
                "  • Ubuntu/Debian: sudo apt install python3\n"
                "  • Fedora: sudo dnf install python3\n"
                "  • Arch: sudo pacman -S python\n"
                "  • Termux: pkg install python"
            )
            return 1
        
        # 5. Prepare system (install venv if needed)
        preparator = SystemPreparator(env)
        
        if not env.venv_available:
            InstallerUI.show_step("Instalando python-venv", "📦")
            if not preparator.install_venv_package():
                InstallerUI.show_error(
                    "No se pudo instalar python3-venv.\n"
                    f"Intenta manualmente: sudo {env.pkg_install_cmd} python3-venv"
                )
                return 1
            InstallerUI.show_step_done("python-venv instalado")
        
        # 6. Install Termux dependencies if needed
        if env.is_termux:
            InstallerUI.show_step("Instalando dependencias de Termux", "📱")
            preparator.install_termux_deps()
            InstallerUI.show_step_done()
        
        # 7. Create virtual environment
        InstallerUI.show_step("Creando entorno virtual", "🐍")
        print(f"       {Colors.DIM}Ubicación: {VENV_DIR}{Colors.RESET}")
        
        venv_manager = VirtualEnvManager(env, VENV_DIR)
        
        if not venv_manager.create_venv():
            InstallerUI.show_error("No se pudo crear el entorno virtual.")
            return 1
        InstallerUI.show_step_done("Entorno virtual creado")
        
        # 8. Upgrade pip
        InstallerUI.show_step("Actualizando pip", "📦")
        venv_manager.upgrade_pip()
        InstallerUI.show_step_done("pip actualizado")
        
        # 9. Install kr-cli-dominion with live progress
        time.sleep(0.5)
        success = venv_manager.install_package(PACKAGE_NAME)
        
        if not success:
            InstallerUI.show_error(
                "La instalación falló.\n"
                "Intenta ejecutar manualmente:\n"
                f"  {venv_manager.venv_pip} install {PACKAGE_NAME}"
            )
            return 1
        
        # 10. Show success and instructions
        InstallerUI.show_final_success(INSTALL_DIR, venv_manager, env)
        
        # 11. Ask to launch
        if InstallerUI.ask_launch(INSTALL_DIR):
            launch_kr_clidn(INSTALL_DIR, venv_manager, env)
        else:
            print(f"\n    {Colors.BRIGHT_GREEN}✓ Instalación completada.{Colors.RESET}")
            print(f"    {Colors.DIM}Para ejecutar después:{Colors.RESET}")
            print(f"    {Colors.BRIGHT_WHITE}cd {INSTALL_DIR} && source venv/bin/activate && kr-clidn{Colors.RESET}\n")
        
        return 0
            
    except KeyboardInterrupt:
        print(f"\n\n    {Colors.YELLOW}⚠ Instalación cancelada por el usuario{Colors.RESET}\n")
        return 130
    except Exception as e:
        InstallerUI.show_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

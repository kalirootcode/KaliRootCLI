"""
Distribution Detector for KaliRoot CLI
Professional grade system detection for security context awareness.
"""

import os
import sys
import shutil
import subprocess
import platform
import logging
import webbrowser
from dataclasses import dataclass
from typing import Literal, Optional

# Setup logger
logger = logging.getLogger(__name__)

DistroType = Literal["termux", "kali", "debian", "ubuntu", "generic"]

@dataclass
class SystemContext:
    """Detailed system context for AI awareness."""
    distro: DistroType
    is_rooted: bool
    pkg_manager: str  # 'apt', 'pkg', 'dnf', etc.
    shell: str        # 'bash', 'zsh', 'fish'
    has_sudo: bool
    home_dir: str
    username: str

class DistroDetector:
    """
    Advanced system detector.
    Analyzes environment to provide accurate context for security operations.
    """
    
    _instance = None
    _context: Optional[SystemContext] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._analyze()
        return cls._instance
    
    def _analyze(self) -> None:
        """Perform deep system analysis."""
        try:
            # 1. Detect Distro
            distro_type = self._detect_distro_type()
            
            # 2. Check Root/Sudo
            is_rooted = os.geteuid() == 0
            has_sudo = shutil.which("sudo") is not None
            
            # 3. Detect Package Manager
            pkg_manager = self._detect_pkg_manager(distro_type)
            
            # 4. Detect Shell
            shell_path = os.environ.get("SHELL", "/bin/bash")
            shell_name = os.path.basename(shell_path)
            
            # 5. User Info
            username = os.environ.get("USER", "unknown")
            home = os.path.expanduser("~")
            
            self._context = SystemContext(
                distro=distro_type,
                is_rooted=is_rooted,
                has_sudo=has_sudo,
                pkg_manager=pkg_manager,
                shell=shell_name,
                home_dir=home,
                username=username
            )
            
            logger.info(f"System Context: {self._context}")
            
        except Exception as e:
            logger.error(f"Error analyzing system: {e}")
            # Fallback safe context
            self._context = SystemContext(
                distro="generic",
                is_rooted=False,
                has_sudo=False,
                pkg_manager="unknown",
                shell="bash",
                home_dir="/tmp",
                username="unknown"
            )
    
    def _detect_distro_type(self) -> DistroType:
        """Identify specific distribution."""
        # Termux check (most distinct)
        if "/com.termux/" in os.environ.get("PREFIX", "") or os.path.exists("/data/data/com.termux"):
            return "termux"
            
        # Linux checks
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    if "kali" in content:
                        return "kali"
                    elif "ubuntu" in content:
                        return "ubuntu"
                    elif "debian" in content:
                        return "debian"
        except Exception:
            pass
            
        return "generic"
    
    def _detect_pkg_manager(self, distro: DistroType) -> str:
        """Identify available package manager."""
        if distro == "termux":
            return "pkg"
            
        managers = ["apt", "dnf", "pacman", "yum"]
        for mgr in managers:
            if shutil.which(mgr):
                return mgr
        
        return "unknown"
    
    @property
    def context(self) -> SystemContext:
        """Get the full system context."""
        return self._context
    
    @property
    def distro(self) -> DistroType:
        return self._context.distro
    
    def is_termux(self) -> bool:
        return self._context.distro == "termux"
    
    def is_kali(self) -> bool:
        return self._context.distro == "kali"
        
    def get_data_dir(self) -> str:
        """Get secure data directory."""
        if self.is_termux():
            prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
            data_dir = os.path.join(prefix, "var", "lib", "kalirootcli")
        else:
            data_dir = os.path.join(self._context.home_dir, ".local", "share", "kalirootcli")
        
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
        
    def get_config_dir(self) -> str:
        """Get secure config directory."""
        if self.is_termux():
            prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
            config_dir = os.path.join(prefix, "etc", "kalirootcli")
        else:
            config_dir = os.path.join(self._context.home_dir, ".config", "kalirootcli")
        
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def get_session_file(self) -> str:
        return os.path.join(self.get_data_dir(), "session.json")
    
    def open_url(self, url: str) -> bool:
        """Secure URL opener with multiple fallbacks."""
        try:
            if self.is_termux():
                # Termux specific opener
                if shutil.which("termux-open-url"):
                    subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                # Fallback to Android Intent
                result = subprocess.run(
                    ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                return result.returncode == 0
            else:
                # Try platform-specific first
                opened = False
                if sys.platform == 'darwin':
                    result = subprocess.run(['open', url], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    opened = result.returncode == 0
                elif sys.platform == 'win32':
                    os.startfile(url)
                    opened = True
                else:
                    # Generic Linux - try xdg-open first
                    if shutil.which('xdg-open'):
                        result = subprocess.run(['xdg-open', url], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                        opened = result.returncode == 0
                
                # Fallback to Python webbrowser module
                if not opened:
                    webbrowser.open(url)
                    opened = True
                
                return opened
        except Exception as e:
            # Final fallback
            try:
                webbrowser.open(url)
                return True
            except:
                return False

    def get_system_info(self) -> dict:
        """Format system info for display."""
        ctx = self._context
        return {
            "distro": ctx.distro.title(),
            "root": "✅ Yes" if ctx.is_rooted else "❌ No",
            "pkg_manager": ctx.pkg_manager,
            "shell": ctx.shell,
            "user": ctx.username
        }

    def get_distro_emoji(self) -> str:
        emojis = {
            "termux": "📱",
            "kali": "🐉",
            "ubuntu": "🟠",
            "debian": "🌀"
        }
        return emojis.get(self._context.distro, "💻")

    def get_distro_name(self) -> str:
        names = {
            "termux": "Termux (Android)",
            "kali": "Kali Linux",
            "ubuntu": "Ubuntu Linux",
            "debian": "Debian Linux"
        }
        return names.get(self._context.distro, "Generic Linux")


# Global instance
detector = DistroDetector()

# Convenience exports
detect = lambda: detector.distro
is_termux = detector.is_termux
is_kali = detector.is_kali
open_url = detector.open_url

"""
Distribution Detector for KaliRoot CLI
Detects whether running on Termux, Kali Linux, or generic Linux
and provides environment-specific functionality.
"""

import os
import subprocess
import platform
from typing import Literal

DistroType = Literal["termux", "kali", "linux"]


class DistroDetector:
    """Detects the current Linux distribution/environment."""
    
    _instance = None
    _distro: DistroType = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._detect()
        return cls._instance
    
    def _detect(self) -> None:
        """Detect the current environment."""
        # Check for Termux
        prefix = os.environ.get("PREFIX", "")
        if "/com.termux/" in prefix or os.path.exists("/data/data/com.termux"):
            self._distro = "termux"
            return
        
        # Check for Kali Linux
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    if "kali" in content:
                        self._distro = "kali"
                        return
        except Exception:
            pass
        
        # Default to generic Linux
        self._distro = "linux"
    
    @property
    def distro(self) -> DistroType:
        """Get detected distribution."""
        return self._distro
    
    def is_termux(self) -> bool:
        """Check if running on Termux."""
        return self._distro == "termux"
    
    def is_kali(self) -> bool:
        """Check if running on Kali Linux."""
        return self._distro == "kali"
    
    def get_data_dir(self) -> str:
        """
        Get the data directory for storing session and config.
        Creates directory if it doesn't exist.
        """
        if self._distro == "termux":
            prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
            data_dir = os.path.join(prefix, "var", "lib", "kalirootcli")
        else:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".local", "share", "kalirootcli")
        
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def get_config_dir(self) -> str:
        """
        Get the config directory.
        Creates directory if it doesn't exist.
        """
        if self._distro == "termux":
            prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
            config_dir = os.path.join(prefix, "etc", "kalirootcli")
        else:
            home = os.path.expanduser("~")
            config_dir = os.path.join(home, ".config", "kalirootcli")
        
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_session_file(self) -> str:
        """Get path to session file."""
        return os.path.join(self.get_data_dir(), "session.json")
    
    def open_url(self, url: str) -> bool:
        """
        Open a URL in the default browser.
        Uses termux-open-url on Termux, xdg-open on Linux.
        
        Returns True if successful, False otherwise.
        """
        try:
            if self._distro == "termux":
                # Try termux-open-url first
                result = subprocess.run(
                    ["termux-open-url", url],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True
                
                # Fallback to am start
                subprocess.run(
                    ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                    capture_output=True,
                    timeout=5
                )
                return True
            else:
                # Linux - use xdg-open
                subprocess.run(
                    ["xdg-open", url],
                    capture_output=True,
                    timeout=5
                )
                return True
        except Exception:
            return False
    
    def get_system_info(self) -> dict:
        """Get system information for display."""
        info = {
            "distro": self._distro,
            "platform": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
        }
        
        if self._distro == "termux":
            info["prefix"] = os.environ.get("PREFIX", "N/A")
        
        return info
    
    def get_distro_name(self) -> str:
        """Get human-readable distro name."""
        names = {
            "termux": "Termux (Android)",
            "kali": "Kali Linux",
            "linux": "Linux",
        }
        return names.get(self._distro, "Unknown")
    
    def get_distro_emoji(self) -> str:
        """Get emoji for the distro."""
        emojis = {
            "termux": "📱",
            "kali": "🐉",
            "linux": "🐧",
        }
        return emojis.get(self._distro, "💻")


# Singleton instance
detector = DistroDetector()


def detect() -> DistroType:
    """Convenience function to detect distro."""
    return detector.distro


def is_termux() -> bool:
    """Convenience function to check if Termux."""
    return detector.is_termux()


def is_kali() -> bool:
    """Convenience function to check if Kali."""
    return detector.is_kali()


def open_url(url: str) -> bool:
    """Convenience function to open URL."""
    return detector.open_url(url)

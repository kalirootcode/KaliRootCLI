"""
System Collector for KaliRoot CLI
Comprehensive system information gathering with IP/VPN detection.
"""

import os
import sys
import socket
import hashlib
import platform
import subprocess
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SystemInfo:
    """Complete system information structure."""
    # Network
    public_ip: Optional[str] = None
    local_ip: Optional[str] = None
    is_vpn: bool = False
    vpn_interface: Optional[str] = None
    
    # System
    hostname: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    kernel_version: Optional[str] = None
    
    # Hardware
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    ram_total_gb: Optional[float] = None
    disk_total_gb: Optional[float] = None
    
    # Environment
    distro: Optional[str] = None
    shell: Optional[str] = None
    terminal: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
    python_version: Optional[str] = None
    screen_resolution: Optional[str] = None
    
    # Fingerprint
    machine_fingerprint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return asdict(self)


class SystemCollector:
    """
    Collects comprehensive system information.
    Used for security tracking, analytics, and user session logging.
    """
    
    _instance = None
    _info: Optional[SystemInfo] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def collect(self, include_ip: bool = True) -> SystemInfo:
        """
        Collect all system information.
        
        Args:
            include_ip: Whether to fetch public IP (requires internet)
        
        Returns:
            SystemInfo dataclass with all collected data
        """
        info = SystemInfo()
        
        # Network info
        if include_ip:
            info.public_ip = self._get_public_ip()
        info.local_ip = self._get_local_ip()
        info.is_vpn, info.vpn_interface = self._detect_vpn()
        
        # System info
        info.hostname = self._get_hostname()
        info.os_name, info.os_version = self._get_os_info()
        info.kernel_version = self._get_kernel_version()
        
        # Hardware
        info.cpu_model = self._get_cpu_model()
        info.cpu_cores = self._get_cpu_cores()
        info.ram_total_gb = self._get_ram_total()
        info.disk_total_gb = self._get_disk_total()
        
        # Environment
        info.distro = self._get_distro()
        info.shell = self._get_shell()
        info.terminal = self._get_terminal()
        info.timezone = self._get_timezone()
        info.locale = self._get_locale()
        info.python_version = self._get_python_version()
        info.screen_resolution = self._get_screen_resolution()
        
        # Generate fingerprint
        info.machine_fingerprint = self._generate_fingerprint(info)
        
        self._info = info
        return info
    
    @property
    def info(self) -> Optional[SystemInfo]:
        """Get cached system info."""
        return self._info
    
    # ═══════════════════════════════════════════════════════════════════════
    # NETWORK INFO
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_public_ip(self) -> Optional[str]:
        """Get public IP address via external service."""
        import urllib.request
        
        services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ifconfig.me/ip"
        ]
        
        for service in services:
            try:
                with urllib.request.urlopen(service, timeout=5) as response:
                    ip = response.read().decode('utf-8').strip()
                    if ip:
                        return ip
            except Exception:
                continue
        
        return None
    
    def _get_local_ip(self) -> Optional[str]:
        """Get local/private IP address."""
        try:
            # Create a socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return None
    
    def _detect_vpn(self) -> tuple[bool, Optional[str]]:
        """
        Detect if VPN is active by checking for tun/tap interfaces.
        
        Returns:
            Tuple of (is_vpn: bool, vpn_interface: str or None)
        """
        vpn_interfaces = ['tun', 'tap', 'wg', 'ppp', 'vpn']
        
        try:
            # Linux/Unix - check /sys/class/net
            if os.path.exists('/sys/class/net'):
                for iface in os.listdir('/sys/class/net'):
                    for vpn_prefix in vpn_interfaces:
                        if iface.startswith(vpn_prefix):
                            return True, iface
            
            # Alternative: use ip command
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                for vpn_prefix in vpn_interfaces:
                    if vpn_prefix in line.lower():
                        # Extract interface name
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface = parts[1].strip().split('@')[0]
                            return True, iface
            
        except Exception as e:
            logger.debug(f"VPN detection failed: {e}")
        
        return False, None
    
    # ═══════════════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_hostname(self) -> Optional[str]:
        """Get system hostname."""
        try:
            return socket.gethostname()
        except Exception:
            return os.environ.get('HOSTNAME')
    
    def _get_os_info(self) -> tuple[Optional[str], Optional[str]]:
        """Get OS name and version."""
        try:
            system = platform.system()
            
            if system == "Linux":
                # Try to get distro info
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release') as f:
                        info = {}
                        for line in f:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                info[key] = value.strip('"')
                        
                        name = info.get('NAME', 'Linux')
                        version = info.get('VERSION_ID', info.get('VERSION', ''))
                        return name, version
                
                return "Linux", platform.release()
            
            elif system == "Darwin":
                return "macOS", platform.mac_ver()[0]
            
            elif system == "Windows":
                return "Windows", platform.version()
            
            return system, platform.version()
            
        except Exception:
            return platform.system(), None
    
    def _get_kernel_version(self) -> Optional[str]:
        """Get kernel version."""
        try:
            return platform.release()
        except Exception:
            return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # HARDWARE INFO
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_cpu_model(self) -> Optional[str]:
        """Get CPU model name."""
        try:
            # Linux
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if 'model name' in line.lower():
                            return line.split(':')[1].strip()
            
            # Fallback to platform
            return platform.processor() or None
            
        except Exception:
            return None
    
    def _get_cpu_cores(self) -> Optional[int]:
        """Get number of CPU cores."""
        try:
            return os.cpu_count()
        except Exception:
            return None
    
    def _get_ram_total(self) -> Optional[float]:
        """Get total RAM in GB."""
        try:
            # Linux
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            # Value is in kB
                            kb = int(line.split()[1])
                            return round(kb / 1024 / 1024, 2)
            
            # Try psutil if available
            try:
                import psutil
                return round(psutil.virtual_memory().total / (1024**3), 2)
            except ImportError:
                pass
                
        except Exception:
            pass
        
        return None
    
    def _get_disk_total(self) -> Optional[float]:
        """Get total disk space in GB."""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return round(total / (1024**3), 2)
        except Exception:
            return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # ENVIRONMENT INFO
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_distro(self) -> Optional[str]:
        """Get Linux distribution name."""
        try:
            # Check for Termux first
            if os.path.exists('/data/data/com.termux'):
                return 'Termux'
            
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('ID='):
                            return line.split('=')[1].strip().strip('"').title()
            
            return platform.system()
        except Exception:
            return None
    
    def _get_shell(self) -> Optional[str]:
        """Get current shell."""
        try:
            shell_path = os.environ.get('SHELL', '')
            return os.path.basename(shell_path) if shell_path else None
        except Exception:
            return None
    
    def _get_terminal(self) -> Optional[str]:
        """Get terminal emulator info."""
        try:
            # Common terminal environment variables
            for var in ['TERM_PROGRAM', 'TERMINAL', 'TERM']:
                val = os.environ.get(var)
                if val:
                    return val
            return None
        except Exception:
            return None
    
    def _get_timezone(self) -> Optional[str]:
        """Get system timezone."""
        try:
            import time
            return time.tzname[0]
        except Exception:
            return os.environ.get('TZ')
    
    def _get_locale(self) -> Optional[str]:
        """Get system locale."""
        try:
            return os.environ.get('LANG', os.environ.get('LC_ALL'))
        except Exception:
            return None
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_screen_resolution(self) -> Optional[str]:
        """Get screen resolution if available."""
        try:
            # Try xrandr on Linux
            result = subprocess.run(
                ['xrandr', '--current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if '*' in line:
                    # Extract resolution like "1920x1080"
                    parts = line.strip().split()
                    if parts:
                        return parts[0]
            
        except Exception:
            pass
        
        # Try environment variable
        return os.environ.get('DISPLAY')
    
    # ═══════════════════════════════════════════════════════════════════════
    # FINGERPRINTING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _generate_fingerprint(self, info: SystemInfo) -> str:
        """
        Generate a non-reversible machine fingerprint.
        Uses a hash of stable system characteristics.
        """
        try:
            # Combine stable identifiers
            components = [
                info.hostname or '',
                info.cpu_model or '',
                str(info.cpu_cores or ''),
                str(info.ram_total_gb or ''),
                info.os_name or '',
                self._get_machine_id() or ''
            ]
            
            # Create hash
            combined = '|'.join(components)
            fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:32]
            
            return fingerprint
            
        except Exception:
            return hashlib.sha256(str(os.urandom(16)).encode()).hexdigest()[:32]
    
    def _get_machine_id(self) -> Optional[str]:
        """Get machine ID (Linux only)."""
        try:
            # Linux machine-id
            for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
                if os.path.exists(path):
                    with open(path) as f:
                        return f.read().strip()
        except Exception:
            pass
        return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # DISPLAY HELPERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_masked_ip(self, ip: Optional[str]) -> str:
        """Mask IP address for display (show only first and last octet)."""
        if not ip:
            return "Unknown"
        
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.***.***.{parts[3]}"
        return ip[:8] + "..."
    
    def get_display_summary(self) -> Dict[str, str]:
        """Get formatted summary for UI display."""
        if not self._info:
            self.collect()
        
        info = self._info
        
        return {
            "ip": self.get_masked_ip(info.public_ip),
            "vpn_status": "🔒 VPN ACTIVE" if info.is_vpn else "⚠️ NO VPN",
            "vpn_interface": info.vpn_interface or "",
            "os": f"{info.os_name or 'Unknown'} {info.os_version or ''}".strip(),
            "cpu": f"{info.cpu_model or 'Unknown CPU'} | {info.cpu_cores or '?'} cores",
            "ram": f"{info.ram_total_gb or '?'} GB",
            "hostname": info.hostname or "unknown",
            "distro": info.distro or "Unknown"
        }


# Global instance
system_collector = SystemCollector()

# Convenience function
def collect_system_info(include_ip: bool = True) -> SystemInfo:
    """Collect and return system information."""
    return system_collector.collect(include_ip=include_ip)

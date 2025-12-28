"""
Platform Detection and Cross-Platform Utilities.
Supports Kali Linux, Termux, and other Linux distributions.
"""

import os
import sys
import shutil
import subprocess
import platform
from typing import Optional, Tuple


def is_termux() -> bool:
    """
    Detect if running in Termux environment.
    
    Returns:
        True if running in Termux, False otherwise
    """
    # Check for Termux-specific environment variables
    if os.environ.get('TERMUX_VERSION'):
        return True
    
    # Check for Termux-specific paths
    if os.path.exists('/data/data/com.termux'):
        return True
    
    # Check if PREFIX points to Termux
    prefix = os.environ.get('PREFIX', '')
    if '/com.termux' in prefix:
        return True
    
    # Check for termux-specific commands
    if shutil.which('termux-info'):
        return True
    
    return False


def is_kali_linux() -> bool:
    """
    Detect if running on Kali Linux.
    
    Returns:
        True if running on Kali Linux, False otherwise
    """
    # Check /etc/os-release for Kali
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read().lower()
            if 'kali' in content:
                return True
    except (FileNotFoundError, PermissionError):
        pass
    
    # Check for Kali-specific paths
    if os.path.exists('/usr/share/kali-themes'):
        return True
    
    return False


def get_platform_name() -> str:
    """
    Get human-readable platform name.
    
    Returns:
        Platform name (e.g., "Termux", "Kali Linux", "Linux", "Unknown")
    """
    if is_termux():
        return "Termux"
    elif is_kali_linux():
        return "Kali Linux"
    elif platform.system() == "Linux":
        # Try to get distro name
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('NAME='):
                        name = line.split('=')[1].strip().strip('"')
                        return name
        except:
            pass
        return "Linux"
    elif platform.system() == "Darwin":
        return "macOS"
    elif platform.system() == "Windows":
        return "Windows"
    else:
        return "Unknown"


def get_browser_command() -> Optional[str]:
    """
    Get the appropriate browser command for the current platform.
    
    Returns:
        Browser command string or None if no browser available
    """
    if is_termux():
        # Termux uses termux-open-url
        if shutil.which('termux-open-url'):
            return 'termux-open-url'
        return None
    
    # Try common Linux browser openers
    for cmd in ['xdg-open', 'gnome-open', 'kde-open', 'firefox', 'chromium', 'google-chrome']:
        if shutil.which(cmd):
            return cmd
    
    return None


def open_url_platform_aware(url: str) -> Tuple[bool, str]:
    """
    Open URL using platform-appropriate method.
    
    Args:
        url: URL to open
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate URL
    if not url or not url.startswith(('http://', 'https://')):
        return False, "URL inválida"
    
    browser_cmd = get_browser_command()
    
    if browser_cmd:
        try:
            # Use subprocess for better control
            subprocess.Popen(
                [browser_cmd, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True, f"Abriendo con {browser_cmd}"
        except Exception as e:
            pass
    
    # Fallback to Python's webbrowser module
    try:
        import webbrowser
        webbrowser.open(url)
        return True, "Abriendo navegador predeterminado"
    except Exception as e:
        pass
    
    # If all else fails, try to copy to clipboard
    if try_copy_to_clipboard(url):
        return False, f"URL copiada al portapapeles: {url}"
    
    return False, f"No se pudo abrir. URL: {url}"


def try_copy_to_clipboard(text: str) -> bool:
    """
    Try to copy text to clipboard using platform-specific methods.
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    if is_termux():
        # Termux clipboard
        if shutil.which('termux-clipboard-set'):
            try:
                subprocess.run(
                    ['termux-clipboard-set'],
                    input=text.encode(),
                    check=True,
                    capture_output=True
                )
                return True
            except:
                pass
    
    # Try xclip (Linux)
    if shutil.which('xclip'):
        try:
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=text.encode(),
                check=True,
                capture_output=True
            )
            return True
        except:
            pass
    
    # Try xsel (Linux)
    if shutil.which('xsel'):
        try:
            subprocess.run(
                ['xsel', '--clipboard', '--input'],
                input=text.encode(),
                check=True,
                capture_output=True
            )
            return True
        except:
            pass
    
    return False


def check_git_available() -> Tuple[bool, str]:
    """
    Check if git is installed and accessible.
    
    Returns:
        Tuple of (available: bool, version_or_error: str)
    """
    if not shutil.which('git'):
        platform_name = get_platform_name()
        if is_termux():
            install_cmd = "pkg install git"
        elif is_kali_linux():
            install_cmd = "sudo apt install git"
        else:
            install_cmd = "apt install git / yum install git"
        
        return False, f"Git no instalado. Ejecuta: {install_cmd}"
    
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except Exception as e:
        return False, f"Error al verificar git: {e}"


def check_network_connectivity(host: str = "github.com", timeout: int = 5) -> bool:
    """
    Check if network is accessible.
    
    Args:
        host: Host to ping
        timeout: Timeout in seconds
        
    Returns:
        True if network is accessible, False otherwise
    """
    try:
        # Try to resolve DNS
        import socket
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(host)
        return True
    except:
        return False


def get_install_directory() -> str:
    """
    Get appropriate installation directory for the current platform.
    
    Returns:
        Path to installation directory
    """
    home = os.path.expanduser("~")
    
    if is_termux():
        # Termux has specific storage locations
        # Use $HOME/kaliroot_tools which is accessible
        return os.path.join(home, "kaliroot_tools")
    else:
        # Standard Linux/Kali
        return os.path.join(home, "kaliroot_tools")


def ensure_directory_writable(path: str) -> Tuple[bool, str]:
    """
    Ensure directory exists and is writable.
    
    Args:
        path: Directory path
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        os.makedirs(path, exist_ok=True)
        
        # Test write permissions
        test_file = os.path.join(path, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True, "Directorio accesible"
        except PermissionError:
            return False, f"Sin permisos de escritura en: {path}"
            
    except Exception as e:
        return False, f"Error creando directorio: {e}"


# Platform info for debugging
def get_platform_info() -> dict:
    """
    Get comprehensive platform information.
    
    Returns:
        Dictionary with platform details
    """
    return {
        'platform': get_platform_name(),
        'is_termux': is_termux(),
        'is_kali': is_kali_linux(),
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'browser_cmd': get_browser_command(),
        'git_available': check_git_available()[0],
        'network_ok': check_network_connectivity(),
    }

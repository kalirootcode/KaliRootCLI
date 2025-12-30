"""
Fsociety Penetration Testing Framework Handler.
Provides installation and launch functionality for fsociety tool.
"""

import os
import subprocess
import shutil
from typing import Tuple

from ..ui.display import (
    console,
    print_header,
    print_success,
    print_error,
    print_info,
    print_warning,
    get_input,
    show_loading,
    confirm
)
from .platform_utils import (
    get_install_directory,
    check_git_available,
    check_network_connectivity,
    ensure_directory_writable,
    get_platform_name
)


class FsocietyHandler:
    """Handler for fsociety penetration testing framework."""
    
    def __init__(self):
        self.install_dir = get_install_directory()
        self.fsociety_path = os.path.join(self.install_dir, "fsociety")
        self.repo_url = "https://github.com/fsociety-team/fsociety"
    
    def is_installed(self) -> bool:
        """Check if fsociety is installed."""
        return os.path.exists(self.fsociety_path) and os.path.exists(os.path.join(self.fsociety_path, "fsociety.py"))
    
    def install(self) -> Tuple[bool, str]:
        """
        Install fsociety framework.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check git
        git_ok, git_msg = check_git_available()
        if not git_ok:
            return False, git_msg
        
        # Check network
        if not check_network_connectivity():
            return False, "Sin conexión a internet"
        
        # Ensure directory writable
        dir_ok, dir_msg = ensure_directory_writable(self.install_dir)
        if not dir_ok:
            return False, dir_msg
        
        try:
            if self.is_installed():
                # Update existing installation
                console.print(f"\n[cyan]🔄 Actualizando fsociety...[/cyan]")
                result = subprocess.run(
                    ["git", "-C", self.fsociety_path, "pull"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    return True, "Fsociety actualizado correctamente"
                else:
                    return False, f"Error al actualizar: {result.stderr}"
            else:
                # Fresh installation
                console.print(f"\n[cyan]📥 Instalando fsociety...[/cyan]")
                console.print(f"[dim]Destino: {self.fsociety_path}[/dim]\n")
                
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", self.repo_url, self.fsociety_path],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    # Install Python dependencies if requirements.txt exists
                    req_file = os.path.join(self.fsociety_path, "requirements.txt")
                    if os.path.exists(req_file):
                        console.print("[cyan]📦 Instalando dependencias...[/cyan]")
                        subprocess.run(
                            ["pip3", "install", "-r", req_file],
                            capture_output=True,
                            timeout=180
                        )
                    
                    return True, f"Fsociety instalado en: {self.fsociety_path}"
                else:
                    return False, f"Error al clonar: {result.stderr}"
                    
        except subprocess.TimeoutExpired:
            return False, "Tiempo de espera agotado"
        except Exception as e:
            return False, f"Error inesperado: {e}"
    
    def launch(self) -> bool:
        """
        Launch fsociety framework.
        
        Returns:
            True if launched successfully, False otherwise
        """
        if not self.is_installed():
            print_error("Fsociety no está instalado")
            return False
        
        fsociety_script = os.path.join(self.fsociety_path, "fsociety.py")
        
        if not os.path.exists(fsociety_script):
            print_error("Script fsociety.py no encontrado")
            return False
        
        try:
            console.print("\n[bold cyan]🚀 Iniciando Fsociety Framework...[/bold cyan]\n")
            console.print("[dim]Presiona Ctrl+C para salir cuando termines[/dim]\n")
            
            # Run fsociety
            subprocess.run(["python3", fsociety_script], cwd=self.fsociety_path)
            return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Fsociety cerrado por el usuario[/yellow]")
            return True
        except Exception as e:
            print_error(f"Error al ejecutar fsociety: {e}")
            return False
    
    def show_info(self):
        """Display comprehensive information about fsociety framework."""
        from rich.panel import Panel
        from rich.columns import Columns
        from rich.text import Text
        from rich.align import Align
        
        # Header with Panel
        header_text = Text()
        header_text.append("🎭 FSOCIETY HACKING FRAMEWORK\n", style="bold white")
        header_text.append("(Inspired by Mr. Robot)", style="dim white")
        
        header_panel = Panel(
            Align.center(header_text),
            border_style="red",
            padding=(0, 2)
        )
        console.print(header_panel)
        console.print()
        
        # Description Panel
        desc_panel = Panel(
            "[bold white]Framework modular de pentesting todo-en-uno.[/bold white]\n"
            "Inspirado en la serie Mr. Robot, fsociety es una suite completa\n"
            "de herramientas para auditorías de seguridad, pentesting y hacking ético.\n\n"
            "[bold cyan]💎 Características principales:[/bold cyan]\n"
            "  • [green]Interfaz interactiva[/green] con menús organizados por categoría\n"
            "  • [green]100+ herramientas[/green] integradas en un solo framework\n"
            "  • [green]Actualizaciones constantes[/green] de la comunidad\n"
            "  • [green]Fácil de usar[/green] - No requiere conocimientos avanzados",
            title="[bold yellow]📖 DESCRIPCIÓN[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(desc_panel)
        
        # Tools Categories
        console.print("\n[bold cyan]🛠️  MÓDULOS Y HERRAMIENTAS INCLUIDAS:[/bold cyan]\n")
        
        # Category 1: Information Gathering
        console.print("[bold green]1. 🔍 INFORMATION GATHERING[/bold green]")
        console.print("   • [cyan]Nmap[/cyan] - Escaneo de redes y puertos")
        console.print("   • [cyan]Setoolkit[/cyan] - Social Engineering Toolkit")
        console.print("   • [cyan]Host To IP[/cyan] - Resolución de dominios")
        console.print("   • [cyan]WPScan[/cyan] - Scanner de WordPress")
        console.print("   • [cyan]CMS Scanner[/cyan] - Detección de CMS")
        console.print("   • [cyan]XSStrike[/cyan] - Detector de XSS")
        console.print("   • [cyan]Dorks[/cyan] - Google Dorks automatizados\n")
        
        # Category 2: Password Attacks
        console.print("[bold green]2. 🔑 PASSWORD ATTACKS[/bold green]")
        console.print("   • [cyan]Cupp[/cyan] - Generador de listas de contraseñas")
        console.print("   • [cyan]Ncrack[/cyan] - Cracker de autenticación de red\n")
        
        # Category 3: Wireless Testing
        console.print("[bold green]3. 📡 WIRELESS TESTING[/bold green]")
        console.print("   • [cyan]Reaver[/cyan] - Ataque WPS")
        console.print("   • [cyan]Pixiewps[/cyan] - Recuperación de PIN WPS")
        console.print("   • [cyan]Bluetooth Honeypot[/cyan] - Seguridad Bluetooth\n")
        
        # Category 4: Exploitation
        console.print("[bold green]4. 💥 EXPLOITATION TOOLS[/bold green]")
        console.print("   • [cyan]SQLMap[/cyan] - Inyección SQL automatizada")
        console.print("   • [cyan]ATSCAN[/cyan] - Scanner de vulnerabilidades")
        console.print("   • [cyan]Shellnoob[/cyan] - Generador de shellcode")
        console.print("   • [cyan]Commix[/cyan] - Inyección de comandos")
        console.print("   • [cyan]FTP Auto Bypass[/cyan] - Bypass de FTP\n")
        
        # Category 5: Sniffing & Spoofing
        console.print("[bold green]5. 🕵️  SNIFFING & SPOOFING[/bold green]")
        console.print("   • [cyan]SSLstrip[/cyan] - Downgrade de HTTPS")
        console.print("   • [cyan]pyPISHER[/cyan] - Phishing automatizado")
        console.print("   • [cyan]SMTP Mailer[/cyan] - Envío de emails\n")
        
        # Category 6: Web Hacking
        console.print("[bold green]6. 🌐 WEB HACKING[/bold green]")
        console.print("   • [cyan]Port Scanner[/cyan] - Escaneo de puertos")
        console.print("   • [cyan]Joomla/WordPress Finder[/cyan] - Detección de CMS")
        console.print("   • [cyan]Admin Panel Finder[/cyan] - Búsqueda de paneles")
        console.print("   • [cyan]Zip Files Finder[/cyan] - Archivos expuestos")
        console.print("   • [cyan]Cloudflare Bypass[/cyan] - Bypass de CDN\n")
        
        # Category 7: Post-Exploitation
        console.print("[bold green]7. 🎯 POST-EXPLOITATION[/bold green]")
        console.print("   • [cyan]Shell Checker[/cyan] - Validación de shells")
        console.print("   • [cyan]POET[/cyan] - Post-exploitation framework")
        console.print("   • [cyan]Weema[/cyan] - Web exploitation\n")
        
        # Platform Support
        platform_panel = Panel(
            "[bold white]Plataformas Soportadas:[/bold white]\n\n"
            "✅ [green]Kali Linux[/green] - Soporte completo nativo\n"
            "✅ [green]Ubuntu/Debian[/green] - Compatible con apt\n"
            "✅ [green]Arch Linux[/green] - Compatible con pacman\n"
            "✅ [green]Termux (Android)[/green] - Pentesting móvil\n"
            "✅ [green]Windows WSL[/green] - Subsistema Linux\n"
            "✅ [green]Docker[/green] - Contenedores aislados",
            title="[bold cyan]🌐 COMPATIBILIDAD[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(platform_panel)
        
        # Installation Status
        if self.is_installed():
            status_panel = Panel(
                f"[bold green]✅ INSTALADO[/bold green]\n\n"
                f"📂 Ubicación: [cyan]{self.fsociety_path}[/cyan]\n"
                f"🔗 Repositorio: [blue]{self.repo_url}[/blue]\n\n"
                f"[dim]Puedes ejecutar fsociety o actualizarlo desde este menú.[/dim]",
                title="[bold green]📊 ESTADO[/bold green]",
                border_style="green",
                padding=(1, 2)
            )
        else:
            status_panel = Panel(
                "[bold yellow]⚠️  NO INSTALADO[/bold yellow]\n\n"
                "Fsociety no está instalado en tu sistema.\n"
                "Selecciona la opción de instalación para comenzar.\n\n"
                "[bold cyan]💡 Tip:[/bold cyan] La instalación es rápida y automática.\n"
                "[dim]Se descargará el framework y todas sus dependencias.[/dim]",
                title="[bold yellow]📊 ESTADO[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
        console.print(status_panel)
    
    def show_installation_guide(self):
        """Display detailed installation instructions for different platforms."""
        from rich.panel import Panel
        from rich.syntax import Syntax
        from ..ui.display import clear_screen
        
        clear_screen()
        console.print("\n[bold cyan]════════════════════════════════════════════════════════════════[/bold cyan]")
        console.print("[bold white]           📚 GUÍA DE INSTALACIÓN DE FSOCIETY           [/bold white]")
        console.print("[bold cyan]════════════════════════════════════════════════════════════════[/bold cyan]\n")
        
        # Method 1: KaliRoot CLI (Recommended)
        method1 = Panel(
            "[bold green]✨ MÉTODO RECOMENDADO - Instalación automática[/bold green]\n\n"
            "[bold white]Desde este menú:[/bold white]\n"
            "1. Selecciona opción [cyan]'1'[/cyan] para instalar\n"
            "2. Espera a que se descargue y configure\n"
            "3. ¡Listo! Ejecuta con opción [cyan]'1'[/cyan]\n\n"
            "[bold yellow]Ventajas:[/bold yellow]\n"
            "  ✅ Instalación con un solo clic\n"
            "  ✅ Configuración automática de dependencias\n"
            "  ✅ Actualizaciones integradas\n"
            "  ✅ Compatible con Kali Linux y Termux",
            title="[bold green]🚀 OPCIÓN 1: KaliRoot CLI[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(method1)
        
        # Method 2: Manual Installation - Kali/Ubuntu/Debian
        console.print("\n[bold cyan]📦 KALI LINUX / UBUNTU / DEBIAN[/bold cyan]\n")
        kali_commands = """# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install git python3 python3-pip -y

# Clonar repositorio
git clone https://github.com/fsociety-team/fsociety
cd fsociety

# Instalar dependencias Python
pip3 install -r requirements.txt

# Ejecutar
python3 fsociety.py"""
        
        syntax_kali = Syntax(kali_commands, "bash", theme="monokai", line_numbers=False)
        console.print(Panel(syntax_kali, border_style="cyan", padding=(1, 2)))
        
        # Termux
        console.print("\n[bold cyan]📱 TERMUX (ANDROID)[/bold cyan]\n")
        termux_commands = """# Actualizar Termux
pkg update && pkg upgrade -y

# Instalar dependencias
pkg install git python -y

# Clonar repositorio
git clone https://github.com/fsociety-team/fsociety
cd fsociety

# Instalar dependencias Python
pip install -r requirements.txt

# Ejecutar
python fsociety.py"""
        
        syntax_termux = Syntax(termux_commands, "bash", theme="monokai", line_numbers=False)
        console.print(Panel(syntax_termux, border_style="cyan", padding=(1, 2)))
        
        # Docker
        console.print("\n[bold cyan]🐳 DOCKER[/bold cyan]\n")
        docker_commands = """# Crear Dockerfile
FROM kalilinux/kali-rolling
RUN apt update && apt install -y git python3 python3-pip
RUN git clone https://github.com/fsociety-team/fsociety
WORKDIR /fsociety
RUN pip3 install -r requirements.txt
CMD ["python3", "fsociety.py"]

# Construir y ejecutar
docker build -t fsociety .
docker run -it fsociety"""
        
        syntax_docker = Syntax(docker_commands, "dockerfile", theme="monokai", line_numbers=False)
        console.print(Panel(syntax_docker, border_style="cyan", padding=(1, 2)))
        
        # Troubleshooting
        troubleshoot = Panel(
            "[bold yellow]⚠️  Problemas comunes y soluciones:[/bold yellow]\n\n"
            "[bold white]1. Error: 'git' no encontrado[/bold white]\n"
            "   → Instala git: [cyan]sudo apt install git[/cyan] (Linux)\n"
            "   → Instala git: [cyan]pkg install git[/cyan] (Termux)\n\n"
            "[bold white]2. Error: 'python3' no encontrado[/bold white]\n"
            "   → Instala Python: [cyan]sudo apt install python3[/cyan]\n\n"
            "[bold white]3. Error: 'pip' no encontrado[/bold white]\n"
            "   → Instala pip: [cyan]sudo apt install python3-pip[/cyan]\n\n"
            "[bold white]4. Error de permisos[/bold white]\n"
            "   → Usa [cyan]sudo[/cyan] para comandos de instalación\n"
            "   → En Termux no necesitas sudo\n\n"
            "[bold white]5. Dependencias faltantes[/bold white]\n"
            "   → Ejecuta: [cyan]pip3 install -r requirements.txt[/cyan]",
            title="[bold red]🔧 SOLUCIÓN DE PROBLEMAS[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(troubleshoot)
        
        console.input("\n[bold cyan]Presiona Enter para volver al menú...[/bold cyan]")


def run_fsociety_menu():
    """Main menu for fsociety tool."""
    from ..ui.display import clear_screen
    
    handler = FsocietyHandler()
    
    while True:
        clear_screen()
        
        # KR-CLI Banner with Fsociety title
        banner_ascii = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""
        from rich.text import Text
        from rich.panel import Panel
        from rich.align import Align
        from rich import box
        from ..ui.colors import STYLE_BLUE_DARK, STYLE_BLUE, STYLE_CYAN, STYLE_TEXT, GRADIENT_BLUE_CYAN
        
        lines = banner_ascii.strip().split("\n")
        banner_rich = Text()
        total_lines = len(lines)
        
        for i, line in enumerate(lines):
            progress = i / max(total_lines - 1, 1)
            color_idx = int(progress * (len(GRADIENT_BLUE_CYAN) - 1))
            color = GRADIENT_BLUE_CYAN[color_idx]
            banner_rich.append(line + "\n", style=f"bold {color}")
        
        centered_banner = Align.center(banner_rich)
        console.print(Panel(
            centered_banner,
            box=box.DOUBLE_EDGE,
            border_style=STYLE_CYAN,
            title=f"[bold {STYLE_TEXT}]🎭 FSOCIETY FRAMEWORK[/bold {STYLE_TEXT}]",
            subtitle=f"[italic {STYLE_CYAN}]Inspired by Mr. Robot[/italic {STYLE_CYAN}]",
            padding=(1, 4)
        ))
        console.print()
        
        handler.show_info()
        
        console.print()  # Spacer
        
        if handler.is_installed():
            print_menu_option("1", "🚀 Ejecutar Fsociety", "Iniciar el framework")
            print_menu_option("2", "🔄 Actualizar", "Actualizar a la última versión")
            print_menu_option("3", "📚 Guía de Instalación", "Ver instrucciones detalladas")
        else:
            print_menu_option("1", "📥 Instalar Fsociety", "Clonar e instalar el framework")
            print_menu_option("2", "📚 Guía de Instalación", "Ver instrucciones detalladas")
        
        print_menu_option("0", "Volver")
        
        console.rule(style="dim rgb(0,255,255)")
        choice = get_input("Selecciona")
        
        if choice == "0":
            break
        elif choice == "1":
            if handler.is_installed():
                # Launch
                clear_screen()
                handler.launch()
                input("\nPresiona Enter para continuar...")
            else:
                # Install
                clear_screen()
                console.print("\n[bold cyan]📥 INSTALANDO FSOCIETY FRAMEWORK...[/bold cyan]\n")
                console.print("[dim]Esto puede tomar unos minutos dependiendo de tu conexión.[/dim]\n")
                
                with show_loading("Descargando e instalando..."):
                    success, message = handler.install()
                
                if success:
                    print_success(message)
                    console.print("\n[bold green]✅ ¡Instalación completada![/bold green]")
                    console.print("[cyan]Ahora puedes ejecutar fsociety desde este menú.[/cyan]\n")
                else:
                    print_error(message)
                    console.print("\n[yellow]💡 Tip: Revisa la guía de instalación para solucionar problemas.[/yellow]\n")
                
                input("Presiona Enter para continuar...")
        elif choice == "2":
            if handler.is_installed():
                # Update
                clear_screen()
                console.print("\n[bold cyan]🔄 ACTUALIZANDO FSOCIETY...[/bold cyan]\n")
                
                with show_loading("Descargando actualizaciones..."):
                    success, message = handler.install()
                
                if success:
                    print_success(message)
                else:
                    print_error(message)
                
                input("\nPresiona Enter para continuar...")
            else:
                # Show installation guide
                handler.show_installation_guide()
        elif choice == "3" and handler.is_installed():
            # Show installation guide
            handler.show_installation_guide()


# Import for menu
from ..ui.display import print_menu_option

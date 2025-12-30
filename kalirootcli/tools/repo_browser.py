"""
Repository Browser Module with AI Integration - Paginated View.
Cross-platform support for Kali Linux and Termux.
"""

import os
import subprocess
import shutil
import math
from typing import Dict, List, Tuple
from rich.panel import Panel
from rich.align import Align
from rich.markdown import Markdown

from ..ui.display import (
    console, 
    print_header, 
    print_menu_option, 
    get_input, 
    show_loading, 
    print_success, 
    print_error,
    confirm,
    print_info,
    print_warning,
    clear_screen
)
from ..api_client import api_client
from .repos_data import TOP_REPOS
from .platform_utils import (
    get_platform_name,
    open_url_platform_aware,
    check_git_available,
    check_network_connectivity,
    get_install_directory,
    ensure_directory_writable,
    is_termux
)

class RepoBrowser:
    """Browses and installs top security repositories with cross-platform support."""
    
    def __init__(self):
        self.repos = sorted(TOP_REPOS, key=lambda x: x['name'])
        self.install_dir = get_install_directory()
        self.page_size = 15
        self.platform_name = get_platform_name()
        self._check_initial_dependencies()
    
    def _check_initial_dependencies(self):
        """Check and warn about missing dependencies."""
        git_ok, git_msg = check_git_available()
        if not git_ok:
            print_warning(f"⚠️  {git_msg}")
            print_info("Algunas funciones pueden no estar disponibles.\\n")
        
    def run(self):
        """Main loop for the browser with pagination."""
        current_page = 0
        total_pages = math.ceil(len(self.repos) / self.page_size)
        
        while True:
            clear_screen()
            
            # KR-CLI Banner with Panel
            banner_ascii = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""
            from rich.text import Text
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
                title=f"[bold {STYLE_TEXT}]📦 GIT ARSENAL - TOP 100+ TOOLS[/bold {STYLE_TEXT}]",
                subtitle=f"[italic {STYLE_CYAN}]Security Tools Repository[/italic {STYLE_CYAN}]",
                padding=(1, 4)
            ))
            console.print()
            
            start_idx = current_page * self.page_size
            end_idx = min(start_idx + self.page_size, len(self.repos))
            page_items = self.repos[start_idx:end_idx]
            
            console.print(f"[dim]Mostrando {start_idx + 1}-{end_idx} de {len(self.repos)} herramientas[/dim]")
            console.print(f"[dim]Página {current_page + 1} de {total_pages}[/dim]\n")
            
            # Display items for current page
            # mapped_index is the visual number (1 to N for this page)
            for i, tool in enumerate(page_items, 1):
                status = "✅" if self._is_installed(tool) else " "
                print_menu_option(str(i), f"{tool['name']}", f"{status} [{tool['category']}]")
            
            console.print()
            
            # Navigation Options
            if current_page < total_pages - 1:
                print_menu_option("N", "Siguiente Página")
            if current_page > 0:
                print_menu_option("P", "Anterior Página")
            
            print_menu_option("S", "🔍 Buscar")
            print_menu_option("0", "Volver")
            
            console.rule(style="dim rgb(0,255,255)")
            choice = get_input("Selecciona").strip().upper()
            
            if choice == "0":
                break
            elif choice == "N" and current_page < total_pages - 1:
                current_page += 1
            elif choice == "P" and current_page > 0:
                current_page -= 1
            elif choice == "S":
                self.search_mode()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(page_items):
                    real_tool = page_items[idx]
                    self.show_tool_page(real_tool)

    def search_mode(self):
        """Search for tools."""
        query = get_input("Buscar herramienta").strip().lower()
        if not query:
            return
            
        results = [r for r in self.repos if query in r['name'].lower() or query in r['category'].lower()]
        
        if not results:
            print_error("No se encontraron resultados.")
            input("Presiona Enter...")
            return
            
        while True:
            clear_screen()
            print_header(f"🔍 Resultados: '{query}'")
            
            for i, tool in enumerate(results, 1):
                status = "✅" if self._is_installed(tool) else " "
                print_menu_option(str(i), f"{tool['name']}", f"{status} [{tool['category']}]")
                
            print_menu_option("0", "Volver")
            
            choice = get_input("Selecciona")
            if choice == "0":
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    self.show_tool_page(results[idx])

    def browse_category(self, category_name: str):
        """Browse tools in a specific category."""
        target_repos = [r for r in self.repos if r['category'].lower() == category_name.lower()]
        
        if not target_repos:
            print_error(f"No se encontraron herramientas en categoría: {category_name}")
            input("Presiona Enter...")
            return

        current_page = 0
        total_pages = math.ceil(len(target_repos) / self.page_size)
        
        while True:
            clear_screen()
            
            # KR-CLI Banner with category name
            banner_ascii = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""
            from rich.text import Text
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
                title=f"[bold {STYLE_TEXT}]📦 {category_name.upper()}[/bold {STYLE_TEXT}]",
                subtitle=f"[italic {STYLE_CYAN}]Security Tools Collection[/italic {STYLE_CYAN}]",
                padding=(1, 4)
            ))
            console.print()
            
            start_idx = current_page * self.page_size
            end_idx = min(start_idx + self.page_size, len(target_repos))
            page_items = target_repos[start_idx:end_idx]
            
            console.print(f"[dim]Mostrando {start_idx + 1}-{end_idx} de {len(target_repos)}[/dim]")
            console.print(f"[dim]Página {current_page + 1} de {total_pages}[/dim]\n")
            
            for i, tool in enumerate(page_items, 1):
                status = "✅" if self._is_installed(tool) else " "
                print_menu_option(str(i), tool['name'], f"{status}")
            
            console.print()
            if current_page < total_pages - 1:
                print_menu_option("N", "Siguiente")
            if current_page > 0:
                print_menu_option("P", "Anterior")
            print_menu_option("0", "Volver")
            
            choice = get_input("Selecciona").strip().upper()
            
            if choice == "0": break
            elif choice == "N" and current_page < total_pages - 1: current_page += 1
            elif choice == "P" and current_page > 0: current_page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(page_items):
                    self.show_tool_page(page_items[idx])

    def show_tool_page(self, tool: Dict):
        """Display tool details with AI description."""
        description = "Cargando descripción..."
        
        # Calculate context for AI
        context_prompt = ""
        if api_client.is_logged_in():
            with show_loading(f"🤖 Analizando {tool['name']}..."):
                query = (
                    f"Actúa como experto en ciberseguridad. Describe la herramienta '{tool['name']}' "
                    f"del repositorio {tool['url']}. \n"
                    f"Estructura la respuesta en Markdown:\n"
                    f"1. **Qué es**: Breve resumen.\n"
                    f"2. **Uso Principal**: Casos de uso (hacking ético).\n"
                    f"3. **Ejemplo**: Un comando básico o escenario de uso.\n"
                    f"Sé directo y técnico."
                )
                res = api_client.ai_query(query, environment={})
                if res["success"]:
                    description = res["data"].get("response", "No description generated.")
        else:
            description = "Conéctate para ver la descripción generada por IA."

        while True:
            clear_screen()
            
            # KR-CLI Banner with tool name
            banner_ascii = """
██╗  ██╗██████╗        ██████╗██╗     ██╗
██║ ██╔╝██╔══██╗      ██╔════╝██║     ██║
█████╔╝ ██████╔╝█████╗██║     ██║     ██║
██╔═██╗ ██╔══██╗╚════╝██║     ██║     ██║
██║  ██╗██║  ██║      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝  ╚═╝       ╚═════╝╚══════╝╚═╝
"""
            from rich.text import Text
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
                title=f"[bold {STYLE_TEXT}]🛠️  {tool['name'].upper()}[/bold {STYLE_TEXT}]",
                subtitle=f"[italic {STYLE_CYAN}]{tool['category']}[/italic {STYLE_CYAN}]",
                padding=(1, 4)
            ))
            console.print()
            
            # Display AI Description
            console.print(Panel(
                Markdown(description),
                title="[bold rgb(0,255,255)]⚡ Análisis DOMINION AI[/bold rgb(0,255,255)]",
                border_style="rgb(0,255,255)",
                padding=(1, 2)
            ))
            
            console.print(f"\n[bold white]📂 Categoría:[/bold white] [cyan]{tool['category']}[/cyan]")
            console.print(f"[bold white]🔗 URL:[/bold white] [blue underline]{tool['url']}[/blue underline]")
            
            is_inst = self._is_installed(tool)
            status_style = "bold green" if is_inst else "bold red"
            status_text = "✅ INSTALADO" if is_inst else "❌ NO INSTALADO"
            console.print(f"[bold white]📊 Estado:[/bold white] [{status_style}]{status_text}[/{status_style}]")
            
            console.print()
            console.rule(style="dim rgb(0,255,255)")
            console.print()
            
            if not is_inst:
                print_menu_option("1", "⬇️  INSTALAR AHORA", "Clonar en ~/kaliroot_tools")
            else:
                print_menu_option("1", "🔄 REINSTALAR / ACTUALIZAR", "git pull")
                
            print_menu_option("2", "🌐 ABRIR EN NAVEGADOR", "Visitar GitHub")
            print_menu_option("0", "Volver")
            
            choice = get_input("Acción")
            
            if choice == "0":
                break
            elif choice == "1":
                self._install_tool(tool)
            elif choice == "2":
                self._open_browser(tool["url"])

    def _is_installed(self, tool: Dict) -> bool:
        """Check if tool is already cloned."""
        path = os.path.join(self.install_dir, tool["name"].replace(" ", "_"))
        # Check if directory exists and has .git folder
        if os.path.exists(path):
            git_dir = os.path.join(path, ".git")
            return os.path.exists(git_dir)
        return False

    def _install_tool(self, tool: Dict):
        """Clone repository with enhanced error handling and platform support."""
        # Check git availability
        git_ok, git_msg = check_git_available()
        if not git_ok:
            print_error(git_msg)
            input("\nPresiona Enter...")
            return
        
        # Check network connectivity
        if not check_network_connectivity():
            print_error("❌ Sin conexión a internet. Verifica tu red.")
            input("\nPresiona Enter...")
            return
        
        # Ensure install directory is writable
        dir_ok, dir_msg = ensure_directory_writable(self.install_dir)
        if not dir_ok:
            print_error(f"❌ {dir_msg}")
            input("\nPresiona Enter...")
            return
        
        target_path = os.path.join(self.install_dir, tool["name"].replace(" ", "_"))
        
        try:
            if os.path.exists(target_path):
                # Check if it's a valid git repo
                git_dir = os.path.join(target_path, ".git")
                if not os.path.exists(git_dir):
                    print_warning(f"⚠️  Directorio existe pero no es un repositorio git válido.")
                    if confirm("¿Deseas eliminarlo y clonar de nuevo?"):
                        shutil.rmtree(target_path)
                    else:
                        return
                else:
                    # Update existing repo
                    with show_loading(f"Actualizando {tool['name']}..."):
                        result = subprocess.run(
                            ["git", "-C", target_path, "pull"],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            print_success("✅ Actualizado correctamente.")
                        else:
                            print_error(f"❌ Error al actualizar: {result.stderr}")
                            if "fatal" in result.stderr.lower():
                                if confirm("¿Deseas eliminar y re-clonar?"):
                                    shutil.rmtree(target_path)
                                    # Fall through to clone
                                else:
                                    input("\nPresiona Enter...")
                                    return
                            else:
                                input("\nPresiona Enter...")
                                return
            
            # Clone new repo (or re-clone after removal)
            if not os.path.exists(target_path):
                console.print(f"\n[cyan]📥 Clonando {tool['name']}...[/cyan]")
                console.print(f"[dim]Destino: {target_path}[/dim]\n")
                
                # Try shallow clone first (faster)
                try:
                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", tool["url"], target_path],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        print_success(f"✅ Instalado correctamente en:\n   {target_path}")
                    else:
                        # If shallow clone fails, try full clone
                        if "does not support" in result.stderr or "shallow" in result.stderr:
                            console.print("[yellow]Clonación superficial no soportada, intentando clonación completa...[/yellow]")
                            result = subprocess.run(
                                ["git", "clone", tool["url"], target_path],
                                capture_output=True,
                                text=True,
                                timeout=600  # 10 minute timeout for full clone
                            )
                            if result.returncode == 0:
                                print_success(f"✅ Instalado correctamente en:\n   {target_path}")
                            else:
                                self._handle_git_error(result.returncode, result.stderr, tool)
                        else:
                            self._handle_git_error(result.returncode, result.stderr, tool)
                            
                except subprocess.TimeoutExpired:
                    print_error("❌ Tiempo de espera agotado. El repositorio es muy grande o la conexión es lenta.")
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
            
            input("\nPresiona Enter para continuar...")
            
        except Exception as e:
            print_error(f"❌ Error inesperado: {e}")
            input("\nPresiona Enter...")
    
    def _handle_git_error(self, returncode: int, stderr: str, tool: Dict):
        """Handle specific git error codes with helpful messages."""
        if returncode == 128:
            if "empty" in stderr.lower():
                print_error("❌ Error 128: El repositorio está vacío o no existe.")
            elif "permission" in stderr.lower() or "denied" in stderr.lower():
                print_error("❌ Error 128: Sin permisos para acceder al repositorio.")
            elif "already exists" in stderr.lower():
                print_error("❌ Error 128: El directorio ya existe.")
            else:
                print_error(f"❌ Error 128: {stderr}")
        elif returncode == 1:
            print_error(f"❌ Error de git: {stderr}")
        else:
            print_error(f"❌ Error {returncode}: {stderr}")
        
        console.print(f"\n[dim]URL: {tool['url']}[/dim]")
        console.print(f"[dim]Puedes intentar clonar manualmente con:[/dim]")
        console.print(f"[yellow]git clone {tool['url']}[/yellow]")

    def _open_browser(self, url: str):
        """Open URL with platform-aware browser support."""
        success, message = open_url_platform_aware(url)
        
        if success:
            print_success(f"✅ {message}")
        else:
            print_warning(f"⚠️  {message}")
            console.print(f"\n[cyan]Copia esta URL:[/cyan]")
            console.print(f"[bold yellow]{url}[/bold yellow]\n")
        
        input("Presiona Enter para continuar...")

def run_repo_browser():
    browser = RepoBrowser()
    browser.run()

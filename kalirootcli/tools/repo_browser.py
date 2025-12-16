"""
Repository Browser Module with AI Integration - Paginated View.
"""

import os
import subprocess
import webbrowser
import math
from typing import Dict, List
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
    print_info
)
from ..api_client import api_client
from .repos_data import TOP_REPOS

class RepoBrowser:
    """Browses and installs top security repositories."""
    
    def __init__(self):
        self.repos = sorted(TOP_REPOS, key=lambda x: x['name'])
        self.install_dir = os.path.expanduser("~/kaliroot_tools")
        self.page_size = 15
        
    def run(self):
        """Main loop for the browser with pagination."""
        current_page = 0
        total_pages = math.ceil(len(self.repos) / self.page_size)
        
        while True:
            console.clear()
            print_header("📦 GIT ARSENAL (TOP 100+)")
            
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
            
            console.rule(style="dim rgb(255,69,0)")
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
            console.clear()
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
            console.clear()
            print_header(f"📦 {category_name.upper()}")
            
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
            console.clear()
            print_header(f"🛠️  {tool['name']}")
            
            # Display AI Description
            # Import Panel inside method to avoid import loop if any
            from rich.panel import Panel 
            console.print(Panel(
                Markdown(description),
                title="[bold rgb(255,69,0)]⚡ Análisis DOMINION AI[/bold rgb(255,69,0)]",
                border_style="rgb(255,69,0)",
                padding=(1, 2)
            ))
            
            console.print(f"\n[bold white]📂 Categoría:[/bold white] [cyan]{tool['category']}[/cyan]")
            console.print(f"[bold white]🔗 URL:[/bold white] [blue underline]{tool['url']}[/blue underline]")
            
            is_inst = self._is_installed(tool)
            status_style = "bold green" if is_inst else "bold red"
            status_text = "✅ INSTALADO" if is_inst else "❌ NO INSTALADO"
            console.print(f"[bold white]📊 Estado:[/bold white] [{status_style}]{status_text}[/{status_style}]")
            
            console.print()
            console.rule(style="dim rgb(255,69,0)")
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
        return os.path.exists(path)

    def _install_tool(self, tool: Dict):
        """Clone the repository."""
        os.makedirs(self.install_dir, exist_ok=True)
        target_path = os.path.join(self.install_dir, tool["name"].replace(" ", "_"))
        
        try:
            if os.path.exists(target_path):
                with show_loading(f"Actualizando en {target_path}..."):
                    subprocess.run(
                        ["git", "-C", target_path, "pull"],
                        check=True,
                        capture_output=True
                    )
                print_success("Actualizado correctamente.")
            else:
                with show_loading(f"Clonando en {target_path}..."):
                    subprocess.run(
                        ["git", "clone", tool["url"], target_path],
                        check=True,
                        capture_output=True
                    )
                print_success(f"Instalado correctamente en:\n{target_path}")
            
            input("\nPresiona Enter para continuar...")
        except subprocess.CalledProcessError as e:
            print_error(f"Error en operación git: {e}")
            input("\nPresiona Enter...")
        except FileNotFoundError:
            print_error("Comando 'git' no encontrado. Instálalo primero.")
            input("\nPresiona Enter...")

    def _open_browser(self, url: str):
        """Open URL in browser."""
        try:
            webbrowser.open(url)
            print_info("Abriendo navegador...")
        except Exception as e:
            print_error(f"No se pudo abrir navegador: {e}")

def run_repo_browser():
    browser = RepoBrowser()
    browser.run()

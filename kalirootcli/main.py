"""
Main entry point for KaliRoot CLI
Professional Cybersecurity CLI with AI, Web Search, and Agent Capabilities.

Version: 5.3.45 - DOMINION
"""

import sys
import os
import time
import logging
from getpass import getpass
import warnings
# Suppress ResourceWarning for cleaner CLI output
warnings.simplefilter("ignore", ResourceWarning)

from typing import Dict, Any

from .api_client import api_client
from .distro_detector import detector
from .ui.display import (
    console, 
    print_banner, 
    print_error, 
    print_success,
    print_info,
    print_warning,
    show_loading,
    print_header,
    print_menu_option,
    print_divider,
    print_ai_response,
    get_input,
    confirm,
    print_panel,
    clear_and_show_banner,
    clear_screen
)

# Import new modules
try:
    from .web_search import web_search, is_search_available
    WEB_SEARCH_AVAILABLE = is_search_available()
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    web_search = None

try:
    from .agent import (
        file_agent, 
        planner, 
        list_templates, 
        list_project_types
    )
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    file_agent = None
    planner = None

# Mobile features (haptics, notifications)
try:
    from .mobile import success_pulse, error_pulse, warning_pulse, payment_success
    HAPTICS_AVAILABLE = True
except ImportError:
    HAPTICS_AVAILABLE = False
    success_pulse = lambda: None
    error_pulse = lambda: None
    warning_pulse = lambda: None
    payment_success = lambda: None

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

def authenticate() -> bool:
    """Handle authentication flow with email verification."""
    import re
    
    def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    if api_client.is_logged_in():
        with show_loading("Verificando sesión..."):
            result = api_client.get_status()
        
        if result["success"]:
            data = result["data"]
            status_text = "[green]PREMIUM[/green]" if data.get("is_premium") else "[yellow]FREE[/yellow]"
            print_success(f"¡Bienvenido de nuevo! [{status_text}]")
            return True
        else:
            print_info("Sesión expirada. Por favor inicia sesión nuevamente.")
            api_client.logout()
    
    while True:
        clear_screen()  # Clean presentation for auth menu
        print_banner()   # Show banner clearly
        console.print("\n[bold cyan]           AUTENTICACIÓN          [/bold cyan]\n")
        
        print_menu_option("1", "🔐 Iniciar Sesión", "Con email verificado")
        print_menu_option("2", "📝 Registrarse", "Requiere verificación por email")
        print_menu_option("0", "❌ Salir")
        
        choice = get_input("Opción")
        
        if choice == "1":
            # LOGIN
            console.print("\n[bold cyan]🔐 INICIAR SESIÓN[/bold cyan]\n")
            email = get_input("📧 Email").lower().strip()
            
            if not email or not is_valid_email(email):
                print_error("Formato de email inválido")
                continue
            
            password = getpass("🔐 Contraseña: ")
            
            with show_loading("Verificando credenciales..."):
                result = api_client.login(email, password)
            
            if result["success"]:
                # Get status to show subscription info
                status_result = api_client.get_status()
                if status_result["success"]:
                    data = status_result["data"]
                    if data.get("is_premium"):
                        console.print(f"\n[bold green]✨ MODO PREMIUM ACTIVO[/bold green]")
                        console.print(f"[dim]Días restantes: {data.get('days_left', 0)}[/dim]")
                    else:
                        console.print(f"\n[yellow]📊 Modo FREE - Créditos: {data.get('credits', 0)}[/yellow]")
                print_success("¡Login exitoso!")
                success_pulse()  # Haptic feedback on mobile
                return True
            else:
                error = result.get("error", "Error de autenticación")
                print_error(error)
                error_pulse()  # Haptic feedback on mobile
                
                # Offer to resend verification
                if "verific" in error.lower():
                    resend = get_input("¿Reenviar correo de verificación? (s/n)").lower()
                    if resend == "s":
                        res = api_client.resend_verification(email)
                        if res.get("success"):
                            print_info("📧 Correo de verificación reenviado")
                        else:
                            print_error("No se pudo reenviar")
                
        elif choice == "2":
            # REGISTER
            console.print("\n[bold cyan]📝 REGISTRO DE USUARIO[/bold cyan]")
            console.print("[dim]Se requiere verificación por correo electrónico[/dim]\n")
            
            email = get_input("📧 Email").lower().strip()
            
            if not email or not is_valid_email(email):
                print_error("Formato de email inválido")
                continue
            
            username = get_input("👤 Username (opcional, Enter para omitir)").strip()
            if not username:
                username = email.split("@")[0]
            
            password = getpass("🔐 Contraseña (mín. 6 caracteres): ")
            if len(password) < 6:
                print_error("La contraseña debe tener al menos 6 caracteres")
                continue
                
            password2 = getpass("🔐 Confirmar contraseña: ")
            if password != password2:
                print_error("Las contraseñas no coinciden")
                continue
            
            with show_loading("Creando cuenta..."):
                result = api_client.register(email, password, username)
            
            if result.get("success"):
                console.print("\n[bold green]═══════════════════════════════════════[/bold green]")
                console.print("[bold green]        ✅ ¡REGISTRO EXITOSO!           [/bold green]")
                console.print("[bold green]═══════════════════════════════════════[/bold green]\n")
                console.print(f"📧 Enviamos un correo a: [cyan]{email}[/cyan]\n")
                console.print("[yellow]⚠️  PASOS SIGUIENTES:[/yellow]")
                console.print("  1. Revisa tu bandeja de entrada (y spam)")
                console.print("  2. Haz clic en el enlace de verificación")
                console.print("  3. Regresa aquí y selecciona 'Iniciar Sesión'\n")
                # Don't auto-login, user must verify email first
            else:
                print_error(result.get("error", "Error en el registro"))
                
        elif choice == "0":
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

def main_menu():
    """Main application menu."""
    running = True
    
    while running:
        with show_loading("Cargando..."):
            status_result = api_client.get_status()
        
        if not status_result["success"]:
            print_error("Error de sesión. Por favor reinicia la aplicación.")
            break
        
        status = status_result["data"]
        sys_info = detector.get_system_info()
        
        clear_screen()
        
        mode = "OPERATIVO" if status.get("is_premium") else "CONSULTA"
        is_premium = status.get("is_premium", False)
        sub_status = (status.get("subscription_status") or "free").lower()
        
        # Logic to handle status display
        if is_premium:
            status_label = " PREMIUM "
            status_color = "bold white on green"
        else:
            if sub_status == "premium":
                # Paid but maybe expired or issue
                status_label = " PENDING / EXPIRED "
                status_color = "bold white on yellow"
            else:
                status_label = " FREE "
                status_color = "bold white on red"
        
        # Header
        print_header("KR-CLI DOMINION v3.0")
        
        # Imports for dashboard
        from rich.align import Align
        from rich.table import Table
        from rich.panel import Panel
        from rich import box
        
        # 1. System Info (Centered & Compact)
        sys_info_text = f"[bold rgb(0,100,255)]OS:[/bold rgb(0,100,255)] {sys_info['distro']}  │  [bold rgb(0,100,255)]Shell:[/bold rgb(0,100,255)] {sys_info['shell']}  │  [bold rgb(0,100,255)]Root:[/bold rgb(0,100,255)] {sys_info['root']}"
        console.print(Align.center(Panel(sys_info_text, border_style="dim rgb(0,255,255)", padding=(0, 2), title="[dim]System[/dim]")))
        
        # 2. User Dashboard (Elegant Grid)
        user_table = Table(show_header=False, box=None, padding=(0, 2))
        user_table.add_column("Key", style="bold rgb(0,100,255)", justify="right")
        user_table.add_column("Value", style="white")
        
        user_table.add_row("Identity 👤", status.get('username') or status.get('email'))
        user_table.add_row("Plan Status 💎", f"[{status_color}]{status_label}[/{status_color}]")
        user_table.add_row("Credits 💳", f"[bold]{status.get('credits', 0)}[/bold]")
        user_table.add_row("Mode ⚙️", mode)
        
        dashboard_panel = Panel(
            user_table,
            title="[bold rgb(0,255,255)] DOMINION DASHBOARD [/bold rgb(0,255,255)]",
            border_style="rgb(0,255,255)",
            padding=(1, 2)
        )
        console.print(dashboard_panel)
        console.print(Align.center("[dim]Modules: 🔍 Web Search  │  🤖 Agent Core[/dim]"))
        
        console.print() # spacer
        
        # Features status
        features = []
        if WEB_SEARCH_AVAILABLE:
            features.append("[green]🔍 Búsqueda Web[/green]")
        if AGENT_AVAILABLE:
            features.append("[green]🤖 Agente[/green]")
        if features:
            console.print(f"[bold]📦 Módulos:[/bold] {' │ '.join(features)}")
        
        print_divider()
        
        # Menu options
        print_menu_option("1", "🧠 CONSOLA AI", "Consultas de seguridad con búsqueda web")
        print_menu_option("2", "🤖 AGENTE MANUAL", "Plantillas y scaffolding")
        print_menu_option("3", "📋 PLANIFICADOR", "Gestión de proyectos y auditorías")
        print_menu_option("4", "🏪 TIENDA", "Obtener acceso Premium y Créditos")
        print_menu_option("5", "⚙️  CONFIGURACIÓN", "Cuenta y ajustes")
        print_menu_option("0", "🚪 SALIR")
        
        print_divider()
        
        choice = get_input("Selecciona")
        
        if choice == "1":
            ai_console(status)
        elif choice == "2":
            agent_menu()
        elif choice == "3":
            planner_menu()
        elif choice == "4":
            upgrade_menu()
        elif choice == "5":
            if settings_menu():
                running = False
        elif choice == "0":
            if confirm("¿Salir de KaliRoot CLI?"):
                running = False
                console.print("\n[bold cyan]👋 ¡Hasta pronto![/bold cyan]\n")


# ═══════════════════════════════════════════════════════════════════════════════
# AI CONSOLE (Enhanced with Web Search)
# ═══════════════════════════════════════════════════════════════════════════════

def ai_console(status: Dict[str, Any]):
    """Enhanced AI interaction interface with web search."""
    mode = "OPERATIVO" if status["is_premium"] else "CONSULTA"
    sys_info = detector.get_system_info()
    
    # Settings for this session
    web_search_enabled = WEB_SEARCH_AVAILABLE
    
    print_header(f"🧠 CONSOLA AI [{mode}]")
    
    # Status display
    if not status["is_premium"]:
        console.print(f"[yellow]💳 Créditos disponibles: {status['credits']}[/yellow]")
        console.print("[dim]Actualiza a Premium para consultas ilimitadas.[/dim]\n")
    else:
        console.print("[green]⭐ Modo Premium - Consultas ilimitadas[/green]\n")
    
    # Web search status
    if WEB_SEARCH_AVAILABLE:
        status_text = "[green]ACTIVA[/green]" if web_search_enabled else "[yellow]DESACTIVADA[/yellow]"
        console.print(f"[bold]🔍 Búsqueda Web:[/bold] {status_text}")
    
    console.print("\n[dim]Comandos especiales:[/dim]")
    console.print("[dim]  /search [query] - Buscar en internet[/dim]")
    console.print("[dim]  /analyze        - Analizar proyecto actual con AI[/dim]")
    console.print("[dim]  /news [topic]   - Últimas noticias de seguridad[/dim]")
    console.print("[dim]  /cve [id]       - Información de CVE[/dim]")
    console.print("[dim]  /websearch      - Toggle búsqueda web[/dim]")
    console.print("[dim]  exit            - Volver al menú[/dim]")
    console.print("\n[dim]💡 Tip: Di 'crear proyecto pentest X' para auto-crear proyectos[/dim]\n")
    
    environment = {
        "distro": sys_info.get("distro", "linux"),
        "shell": sys_info.get("shell", "bash"),
        "root": sys_info.get("root", "No"),
        "pkg_manager": sys_info.get("pkg_manager", "apt")
    }
    
    while True:
        query = get_input("🔮 Query")
        
        if query.lower() in ['exit', 'quit', 'back', 'salir']:
            clear_and_show_banner()
            break
        
        if not query:
            continue
        
        # 1. Handle special commands
        if query.startswith("/"):
            result = handle_special_command(query, web_search_enabled)
            if result == "toggle_search":
                web_search_enabled = not web_search_enabled
                status_text = "[green]ACTIVADA[/green]" if web_search_enabled else "[yellow]DESACTIVADA[/yellow]"
                print_info(f"Búsqueda web: {status_text}")
            continue

        # 2. Handle conversational agent intents (Agentic Mode)
        if AGENT_AVAILABLE:
            intent = file_agent.parse_natural_language_intent(query)
            if intent["action"] == "create_project":
                msg = f"Detectada intención de crear proyecto: {intent['type'].upper()} ({intent['name']})"
                if confirm(msg):
                    with show_loading("Creando proyecto..."):
                        res = file_agent.create_project_structure(intent["name"], intent["type"], intent["description"])
                    if res["success"]:
                        print_success(res["message"])
                        console.print(f"\n[dim]📁 {res['path']}[/dim]")
                    else:
                        print_error(res["error"])
                    continue
        
        # 3. Enrich query with web search if enabled
        enriched_query = query
        web_context = ""
        
        if web_search_enabled and WEB_SEARCH_AVAILABLE:
            # Detect if query needs real-time data
            search_keywords = ["último", "últimas", "reciente", "2024", "2025", "CVE", "exploit", "vulnerabilidad", "actualización"]
            needs_search = any(kw.lower() in query.lower() for kw in search_keywords)
            
            if needs_search:
                with show_loading("🔍 Buscando información actualizada..."):
                    web_context = web_search.search_security(query)
                
                if web_context:
                    console.print("[dim]📡 Datos web obtenidos[/dim]")
                    enriched_query = f"{query}\n\n{web_context}"
        
        # Send to API
        with show_loading("🧠 Procesando..."):
            result = api_client.ai_query(enriched_query, environment)
        
        if result["success"]:
            data = result["data"]
            print_ai_response(data["response"], data["mode"])
            
            if data.get("credits_remaining") is not None:
                console.print(f"[dim]💳 Créditos restantes: {data['credits_remaining']}[/dim]\n")
        else:
            error_msg = result.get("error", "Error desconocido")
            if "credits" in error_msg.lower() or "créditos" in error_msg.lower():
                # Persuasive out-of-credits message
                clear_screen()
                console.print("\n[bold red]😔 ¡Ups! Te quedaste sin créditos...[/bold red]\n")
                console.print("[bold white]Pero estábamos en algo importante.[/bold white]")
                console.print(f"[cyan]Tu consulta era valiosa y DOMINION estaba listo para darte[/cyan]")
                console.print(f"[cyan]información que pocos conocen sobre este tema.[/cyan]\n")
                
                console.print("[bold yellow]🔥 No te quedes a medias:[/bold yellow]")
                console.print("  • La respuesta completa está lista esperando por ti")
                console.print("  • DOMINION tiene el conocimiento que necesitas")
                console.print("  • Un solo paso te separa de continuar aprendiendo\n")
                
                console.print("[bold green]💎 PAQUETES DISPONIBLES:[/bold green]")
                console.print("  💳 [bold]Créditos[/bold]: 200 créditos - $10")
                console.print("  👑 [bold]Premium[/bold]: 500 créditos + herramientas - $20/mes\n")
                
                console.rule(style="yellow")
                print_menu_option("1", "💎 Ver Tienda", "Comprar créditos o Premium")
                print_menu_option("0", "Volver al menú")
                console.rule(style="yellow")
                
                sub_choice = get_input("¿Qué deseas hacer?")
                if sub_choice == "1":
                    upgrade_menu()
                clear_and_show_banner()
                return  # Exit chat session
            else:
                print_error(error_msg)


def handle_special_command(command: str, web_search_enabled: bool) -> str:
    """Handle special CLI commands."""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    
    if cmd == "/analyze" and AGENT_AVAILABLE:
        print_info("Analizando directorio actual...")
        context = file_agent.analyze_project_context()
        
        query = f"""
        Analyze this project context and provide recommendations:
        {context}
        """
        
        with show_loading("🧠 Analizando código y estructura..."):
            result = api_client.ai_query(query, {})
            
        if result["success"]:
            print_ai_response(result["data"]["response"], result["data"]["mode"])
        else:
            print_error(result["error"])
            
    elif cmd == "/search" and WEB_SEARCH_AVAILABLE:
        if not arg:
            print_warning("Uso: /search <query>")
            return ""
        
        with show_loading(f"🔍 Buscando: {arg}..."):
            results = web_search.search(arg)
        
        if results:
            console.print(f"\n[bold cyan]📡 Resultados para '{arg}':[/bold cyan]\n")
            for i, r in enumerate(results, 1):
                console.print(f"[bold]{i}.[/bold] {r.title}")
                console.print(f"   [dim]{r.body[:150]}...[/dim]")
                console.print(f"   [blue underline]{r.url}[/blue underline]\n")
        else:
            print_warning("No se encontraron resultados")
    
    elif cmd == "/news" and WEB_SEARCH_AVAILABLE:
        topic = arg or "cybersecurity"
        
        with show_loading(f"📰 Buscando noticias: {topic}..."):
            results = web_search.search_news(f"{topic} security")
        
        if results:
            console.print(f"\n[bold cyan]📰 Noticias de seguridad:[/bold cyan]\n")
            for r in results[:5]:
                console.print(f"• [bold]{r.title}[/bold]")
                if r.date:
                    console.print(f"  [dim]{r.date}[/dim]")
                console.print(f"  [dim]{r.body[:100]}...[/dim]\n")
        else:
            print_warning("No se encontraron noticias")
    
    elif cmd == "/cve" and WEB_SEARCH_AVAILABLE:
        if not arg:
            print_warning("Uso: /cve <CVE-ID> o /cve <keyword>")
            return ""
        
        with show_loading(f"🛡️ Buscando CVE: {arg}..."):
            if arg.upper().startswith("CVE-"):
                context = web_search.search_cve(cve_id=arg)
            else:
                context = web_search.search_cve(keyword=arg)
        
        if context:
            console.print(context)
        else:
            print_warning("No se encontró información del CVE")
    
    elif cmd == "/websearch":
        return "toggle_search"
    
    elif cmd == "/help":
        console.print("\n[bold cyan]Comandos disponibles:[/bold cyan]")
        console.print("  /search <query>  - Buscar en internet")
        console.print("  /news [topic]    - Noticias de seguridad")
        console.print("  /cve <id>        - Info de CVE")
        console.print("  /websearch       - Toggle búsqueda web")
        console.print("  /help            - Mostrar ayuda")
        console.print("  exit             - Volver al menú\n")
    
    else:
        print_warning(f"Comando no reconocido: {cmd}")
    
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT MODE
# ═══════════════════════════════════════════════════════════════════════════════


# Agent module check
try:
    from .agent import file_agent, list_templates
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

def agent_menu():
    """Agent mode for file and project creation."""
    if not AGENT_AVAILABLE:
        print_error("El módulo de agente no está disponible. Instala las dependencias.")
        get_input("Presiona Enter para continuar...")
        clear_and_show_banner()
        return
    
    while True:
        print_header("🤖 MODO AGENTE")
        
        console.print("[dim]Crea archivos, proyectos y código con plantillas.[/dim]\n")
        
        print_menu_option("1", "📄 Crear Script", "Python o Bash desde plantilla")
        print_menu_option("2", "📁 Crear Proyecto", "Estructura estándar")
        print_menu_option("3", "📋 Ver Proyectos", "Lista de proyectos creados")
        print_menu_option("4", "🔧 Plantillas", "Ver plantillas disponibles")
        print_menu_option("0", "⬅️  Volver")
        
        print_divider()
        
        choice = get_input("Selecciona")
        
        if choice == "1":
            create_script_menu()
        elif choice == "2":
            create_project_menu()
        elif choice == "3":
            list_projects_menu()
        elif choice == "4":
            show_templates()
        elif choice == "0":
            clear_and_show_banner()
            break


def create_script_menu():
    """Create a script from template."""
    print_header("📄 CREAR SCRIPT")
    
    console.print("[bold]Plantillas disponibles:[/bold]")
    templates = list_templates()
    for i, t in enumerate(templates, 1):
        console.print(f"  {i}. {t}")
    
    console.print()
    
    template_choice = get_input("Número de plantilla (o nombre)")
    
    # Handle numeric choice
    try:
        idx = int(template_choice) - 1
        if 0 <= idx < len(templates):
            template_name = templates[idx]
        else:
            print_error("Opción inválida")
            return
    except ValueError:
        template_name = template_choice
    
    if template_name not in templates:
        print_error(f"Plantilla '{template_name}' no encontrada")
        return
    
    name = get_input("Nombre del script")
    if not name:
        print_error("El nombre es requerido")
        return
    
    description = get_input("Descripción (opcional)")
    
    with show_loading("Creando script..."):
        result = file_agent.create_from_template(template_name, name, description)
    
    if result.success:
        print_success(result.message)
        console.print(f"\n[dim]Archivo: {result.path}[/dim]")
    else:
        print_error(result.error)
    
    get_input("\nPresiona Enter para continuar...")
    clear_and_show_banner()


def create_project_menu():
    """Create a project structure."""
    print_header("📁 CREAR PROYECTO")
    
    console.print("[bold]Tipos de proyecto:[/bold]\n")
    
    project_types = list_project_types()
    type_descriptions = {
        "pentest": "Pentesting - Recon, Scan, Exploit, Post, Reports",
        "tool": "Herramienta - src, tests, docs, examples",
        "audit": "Auditoría - Evidence, Reports, Configs",
        "research": "Investigación - Data, Analysis, Papers, PoC",
        "ctf": "CTF - Challenges, Scripts, Flags"
    }
    
    for i, t in enumerate(project_types, 1):
        desc = type_descriptions.get(t, "")
        console.print(f"  [cyan]{i}.[/cyan] [bold]{t.upper()}[/bold]")
        console.print(f"      [dim]{desc}[/dim]")
    
    console.print()
    
    type_choice = get_input("Tipo de proyecto (número o nombre)")
    
    try:
        idx = int(type_choice) - 1
        if 0 <= idx < len(project_types):
            project_type = project_types[idx]
        else:
            print_error("Opción inválida")
            return
    except ValueError:
        project_type = type_choice.lower()
    
    if project_type not in project_types:
        print_error(f"Tipo '{project_type}' no válido")
        return
    
    name = get_input("Nombre del proyecto")
    if not name:
        print_error("El nombre es requerido")
        return
    
    description = get_input("Descripción (opcional)")
    
    with show_loading("Creando proyecto..."):
        result = file_agent.create_project_structure(name, project_type, description)
    
    if result["success"]:
        print_success(result["message"])
        console.print(f"\n[bold]Estructura creada:[/bold]")
        console.print(f"[dim]📁 {result['path']}[/dim]")
        
        console.print("\n[bold]Directorios:[/bold]")
        for d in result["structure"]["directories"]:
            console.print(f"  📂 {d}")
        
        console.print("\n[bold]Archivos:[/bold]")
        for f in result["structure"]["files"]:
            console.print(f"  📄 {f}")
    else:
        print_error(result["error"])
    
    get_input("\nPresiona Enter para continuar...")
    clear_and_show_banner()


def list_projects_menu():
    """List existing projects."""
    print_header("📋 PROYECTOS")
    
    projects = file_agent.list_projects()
    
    if not projects:
        print_info("No hay proyectos creados aún.")
        console.print(f"\n[dim]Directorio base: {file_agent.base_dir}[/dim]")
    else:
        console.print(f"[dim]Total: {len(projects)} proyectos[/dim]\n")
        
        for p in projects:
            type_emoji = {
                "pentest": "🔓",
                "tool": "🔧",
                "audit": "🛡️",
                "research": "🔬",
                "ctf": "🚩"
            }.get(p["type"], "📁")
            
            console.print(f"{type_emoji} [bold]{p['name']}[/bold]")
            console.print(f"   Tipo: {p['type']} │ Modificado: {p['modified']} │ Tamaño: {p['size']}")
            console.print(f"   [dim]{p['path']}[/dim]\n")
    
    get_input("\nPresiona Enter para continuar...")


def show_templates():
    """Show available templates."""
    print_header("🔧 PLANTILLAS DISPONIBLES")
    
    templates = list_templates()
    
    template_info = {
        "python_script": "Script Python con argparse y logging",
        "python_class": "Clase Python con dataclass config",
        "bash_script": "Script Bash profesional con colores",
        "security_audit": "Reporte de auditoría de seguridad",
        "project_plan": "Plan de proyecto estructurado",
        "exploit_template": "Plantilla para exploits (solo educativo)"
    }
    
    for t in templates:
        info = template_info.get(t, "Plantilla personalizada")
        console.print(f"• [bold cyan]{t}[/bold cyan]")
        console.print(f"  [dim]{info}[/dim]\n")
    
    get_input("Presiona Enter para continuar...")
    clear_and_show_banner()


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

def planner_menu():
    """Project planning menu."""
    if not AGENT_AVAILABLE:
        print_error("El módulo de planificación no está disponible.")
        get_input("Presiona Enter para continuar...")
        clear_and_show_banner()
        return
    
    while True:
        print_header("📋 PLANIFICADOR DE PROYECTOS")
        
        print_menu_option("1", "📝 Nuevo Plan", "Crear plan de proyecto")
        print_menu_option("2", "📊 Nuevo Reporte de Auditoría", "Plantilla de auditoría")
        print_menu_option("3", "📋 Ver Planes", "Lista de planes existentes")
        print_menu_option("0", "⬅️  Volver")
        
        print_divider()
        
        choice = get_input("Selecciona")
        
        if choice == "1":
            create_plan_menu()
        elif choice == "2":
            create_audit_menu()
        elif choice == "3":
            list_plans_menu()
        elif choice == "0":
            clear_and_show_banner()
            break


def create_plan_menu():
    """Create a new project plan."""
    print_header("📝 NUEVO PLAN DE PROYECTO")
    
    name = get_input("Nombre del proyecto")
    if not name:
        print_error("El nombre es requerido")
        return
    
    description = get_input("Descripción del proyecto")
    
    console.print("\n[bold]Ingresa los objetivos (uno por línea, vacío para terminar):[/bold]")
    objectives = []
    while True:
        obj = get_input(f"Objetivo {len(objectives) + 1}")
        if not obj:
            break
        objectives.append(obj)
    
    if not objectives:
        objectives = ["Definir objetivos específicos"]
    
    with show_loading("Creando plan..."):
        result = planner.create_plan(name, description, objectives)
    
    if result["success"]:
        print_success(result["message"])
        console.print(f"\n[dim]Archivo: {result['path']}[/dim]")
    else:
        print_error(result.get("error", "Error desconocido"))
    
    get_input("\nPresiona Enter para continuar...")


def create_audit_menu():
    """Create a security audit report."""
    print_header("📊 NUEVO REPORTE DE AUDITORÍA")
    
    name = get_input("Nombre de la auditoría")
    if not name:
        print_error("El nombre es requerido")
        return
    
    description = get_input("Descripción/Alcance")
    
    with show_loading("Creando reporte..."):
        result = planner.create_audit_report(name, description)
    
    if result["success"]:
        print_success(result["message"])
        console.print(f"\n[dim]Archivo: {result['path']}[/dim]")
    else:
        print_error(result.get("error", "Error desconocido"))
    
    get_input("\nPresiona Enter para continuar...")


def list_plans_menu():
    """List existing project plans."""
    print_header("📋 PLANES EXISTENTES")
    
    plans = planner.list_plans()
    
    if not plans:
        print_info("No hay planes creados aún.")
    else:
        for p in plans:
            status_emoji = "🟡" if p["status"] == "planning" else "🟢"
            console.print(f"{status_emoji} [bold]{p['name']}[/bold]")
            console.print(f"   Estado: {p['status']} │ Creado: {p['created'][:10]}")
            console.print(f"   [dim]{p['path']}[/dim]\n")
    
    get_input("\nPresiona Enter para continuar...")
    clear_and_show_banner()


# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE & SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

def show_payment_help():
    """Display comprehensive help about the payment process."""
    clear_screen()
    print_banner(show_skull=False)
    
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white]           🚀 BIENVENIDO AL FUTURO DE LOS PAGOS           [/bold white]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Future vision
    console.print("[bold yellow]💎 EL DINERO DEL FUTURO YA ESTÁ AQUÍ[/bold yellow]")
    console.print("Las [bold green]criptomonedas[/bold green] no son el futuro, [bold]son el presente[/bold].")
    console.print("Gobiernos, bancos y corporaciones ya las usan. ¿Por qué tú no?\\n")
    
    console.print("[dim]• Sin intermediarios bancarios que cobren comisiones abusivas[/dim]")
    console.print("[dim]• Sin límites geográficos ni horarios de atención[/dim]")
    console.print("[dim]• Transacciones en minutos, no días[/dim]")
    console.print("[dim]• TÚ controlas tu dinero, no un banco[/dim]\\n")
    
    console.print("[bold]Dominar las criptomonedas es dominar el futuro financiero.[/bold]")
    console.print("[bold green]Este es tu primer paso hacia la independencia económica digital.[/bold green]\\n")
    
    # Payment method
    console.print("[bold yellow]💳 MÉTODO DE PAGO: SIMPLE Y SEGURO[/bold yellow]")
    console.print("Usamos [bold green]NowPayments[/bold green], procesador líder mundial con +150 criptomonedas.\\n")
    
    console.print("[bold]Moneda aceptada:[/bold] [bold green]USDT (Tether TRC-20)[/bold green]")
    console.print("[dim]Stablecoin 1:1 con USD. Sin volatilidad, máxima estabilidad.[/dim]")
    console.print("[dim]Red TRC-20: Comisiones de $1 USD, confirmación en 3 minutos.[/dim]\\n")
    
    # Global reach
    console.print("[bold yellow]🌍 DISPONIBLE EN TODO EL MUNDO[/bold yellow]")
    console.print("NowPayments opera [bold]sin restricciones geográficas[/bold]. Algunos países:\\n")
    
    regions = [
        "🇺🇸 USA   🇧🇷 BRA   🇦🇷 ARG   🇨🇴 COL   🇲🇽 MEX",
        "🇪🇸 ESP   🇩🇪 DEU   🇫🇷 FRA   🇮🇹 ITA   🇬🇧 GBR",
        "🇨🇳 CHN   🇯🇵 JPN   🇰🇷 KOR   🇮🇳 IND   🇦🇺 AUS",
        "🇨🇦 CAN   🇷🇺 RUS   🇿🇦 ZAF   🇳🇬 NGA   🇦🇪 UAE"
    ]
    
    for row in regions:
        console.print(f"[bold cyan]  {row}[/bold cyan]")
    
    console.print("\\n[dim]América, Europa, Asia, África, Oceanía. Sin fronteras.[/dim]\\n")
    
    # How it works - simplified
    console.print("[bold yellow]⚙️ PROCESO AUTOMATIZADO (3 PASOS)[/bold yellow]\\n")
    
    console.print("[bold cyan]1.[/bold cyan] [bold]Selecciona tu paquete[/bold] → Generamos link único")
    console.print("[bold cyan]2.[/bold cyan] [bold]Envías USDT[/bold] → Desde Binance, Trust Wallet, etc.")
    console.print("[bold cyan]3.[/bold cyan] [bold]¡Listo![/bold] → Créditos acreditados automáticamente\\n")
    
    console.print("[bold green]Todo el proceso toma menos de 5 minutos.[/bold green]")
    console.print("[dim]Sistema IPN (Instant Payment Notification) detecta tu pago en blockchain.[/dim]\\n")
    
    # Premium benefits - technical details
    console.print("[bold yellow]👑 ¿QUÉ OBTIENES CON PREMIUM?[/bold yellow]\\n")
    
    console.print("[bold white]🧠 MODELO IA SUPERIOR[/bold white]")
    console.print("• Free: [dim]Llama 3.1 8B (8 mil millones de parámetros)[/dim]")
    console.print("• Premium: [bold green]Llama 3.3 70B (70 mil millones de parámetros)[/bold green]")
    console.print("  [bold]8.75x más potente[/bold]. Respuestas más precisas y contextuales.\\n")
    
    console.print("[bold white]⚡ CAPACIDADES TÉCNICAS[/bold white]")
    console.print("• [bold]Context Window:[/bold] 128K tokens (equivale a ~300 páginas)")
    console.print("• [bold]Reasoning:[/bold] Análisis profundo de código y vulnerabilidades")
    console.print("• [bold]Tool Calling:[/bold] Ejecución de comandos y scripts avanzados")
    console.print("• [bold]Multi-turn:[/bold] Conversaciones largas con memoria perfecta\\n")
    
    console.print("[bold white]🎯 VENTAJAS OPERATIVAS[/bold white]")
    console.print("• [bold green]Créditos ilimitados[/bold green] - Sin preocuparte por quedarte sin queries")
    console.print("• [bold]Prioridad en respuestas[/bold] - Latencia reducida 40%")
    console.print("• [bold]Acceso a funciones beta[/bold] - Nuevas features antes que nadie")
    console.print("• [bold]Soporte prioritario[/bold] - Respuesta en <24h\\n")
    
    console.print("[bold white]💰 RETORNO DE INVERSIÓN[/bold white]")
    console.print("$20/mes = [bold]~$0.66 por día[/bold]")
    console.print("Menos que un café. Más que una universidad en ciberseguridad.\\n")
    
    # Security
    console.print("[bold yellow]🔒 SEGURIDAD BLOCKCHAIN[/bold yellow]\\n")
    
    console.print("• [bold]Zero-Knowledge:[/bold] No guardamos datos de pago")
    console.print("• [bold]Non-Custodial:[/bold] NowPayments no retiene tus fondos")
    console.print("• [bold]Blockchain Verification:[/bold] Cada pago validado en TRON")
    console.print("• [bold]End-to-End Encryption:[/bold] TLS 1.3 + AES-256\\n")
    
    # Recommended apps
    console.print("[bold yellow]📱 APPS PARA PAGAR (ELIGE UNA)[/bold yellow]")
    console.print("• [bold]Binance[/bold] - Exchange #1 mundial (más fácil para principiantes)")
    console.print("• [bold]Trust Wallet[/bold] - Wallet móvil oficial de Binance")
    console.print("• [bold]MetaMask[/bold] - Wallet para navegador (Chrome/Firefox)")
    console.print("• [bold]Coinbase[/bold] - Exchange regulado USA")
    console.print("• [bold]OKX[/bold] - Exchange con bajas comisiones")
    console.print("• [bold]Bybit[/bold] - Exchange profesional\\n")
    
    console.print("[bold green]💡 CONSEJO:[/bold green] Si no tienes cripto, crea cuenta en Binance.")
    console.print("[dim]   Compra USDT con tarjeta y envíalo a la dirección que te demos.[/dim]\\n")
    
    # Support - Facebook Group
    console.print("[bold yellow]📞 SOPORTE Y COMUNIDAD[/bold yellow]")
    console.print("¿Problemas con el pago? ¿Dudas sobre el programa?")
    console.print("[bold green]Únete a nuestra comunidad en Facebook:[/bold green]\n")
    console.print("[bold cyan]🔗 https://web.facebook.com/share/g/1DNscrsKYp/[/bold cyan]")
    console.print("[dim]Más de 1,000 usuarios activos compartiendo tips y soluciones.[/dim]\n")
    
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white]        El futuro es descentralizado. Únete ahora.        [/bold white]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Interactive menu
    while True:
        console.print("[bold yellow]Opciones:[/bold yellow]")
        console.print("[bold cyan]1[/bold cyan] › Abrir grupo de Facebook")
        console.print("[bold cyan]0[/bold cyan] › Volver al menú principal\n")
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            import webbrowser
            console.print("\n[bold green]✓[/bold green] Abriendo grupo de Facebook en tu navegador...")
            webbrowser.open("https://web.facebook.com/share/g/1DNscrsKYp/")
            time.sleep(2)
            console.print("[dim]Si no se abrió automáticamente, copia el enlace de arriba.[/dim]\n")
        elif choice == "0":
            break
        else:
            console.print("[bold red]✗[/bold red] Opción inválida. Intenta de nuevo.\n")


def upgrade_menu():
    """Handle premium upgrade and credit purchases."""
    from .config import CREDIT_PACKAGES, SUBSCRIPTION_PRICE_USD, SUBSCRIPTION_BONUS_CREDITS
    from rich.panel import Panel
    
    while True:
        clear_screen()
        print_banner(show_skull=False)
        
        # Get current status
        status_res = api_client.get_status()
        is_premium = status_res.get("data", {}).get("is_premium", False) if status_res.get("success") else False
        credits = status_res.get("data", {}).get("credits", 0) if status_res.get("success") else 0
        
        console.print(f"[dim]💳 Tus créditos actuales: {credits}[/dim]\n")
        
        if is_premium:
            console.print("[bold green]✅ Ya eres usuario PREMIUM[/bold green]\n")
        
        console.print("[bold cyan]═══ PAQUETES DISPONIBLES ═══[/bold cyan]\n")
        
        # Display all credit packages
        print_descriptions = [
            "  • [italic]Ideal para iniciarse. Tu primer paso en ciberseguridad.[/italic]",
            "  • [italic]Para estudiantes serios. Profundiza sin límites.[/italic]",
            "  • [italic]Potencia máxima. Para operaciones intensivas.[/italic]"
        ]
        
        for i, pkg in enumerate(CREDIT_PACKAGES, 1):
            emoji = "💳" if i == 1 else "⚡" if i == 2 else "💎"
            desc = print_descriptions[i-1] if i-1 < len(print_descriptions) else ""
            
            console.print(f"[bold yellow]{emoji} PAQUETE {pkg['name'].upper()}[/bold yellow]")
            console.print(f"  • [bold]{pkg['credits']} créditos[/bold] para consultas AI")
            console.print(f"  • Válidos por 30 días")
            console.print(desc)
            console.print(f"  • [bold green]${pkg['price']:.0f} USD (USDT)[/bold green]\n")
        
        # Premium Package
        if not is_premium:
            console.print(Panel(
                f"""
[bold gold1]👑 DOMINION ELITE ARCHITECTURE (PREMIUM)[/bold gold1]

[bold white]Desbloquea el verdadero poder de la Inteligencia Artificial Ofensiva.[/bold white]

[bold cyan]⚡ VENTAJAS TÁCTICAS:[/bold cyan]
 • [bold]1200 CRÉDITOS MENSUALES[/bold] (Recarga automática)
 • [bold]MODELO 70B NEURAL[/bold]: Razonamiento superior y generación de scripts complejos.
 • [bold]SUITE DE HERRAMIENTAS[/bold]: Port Scanner, CVE Lookup & Auto-Exploit Planning.
 • [bold]MODO AGENTE AUTÓNOMO[/bold]: Crea proyectos y estructuras completas con un comando.
 • [bold]MEMORIA INFINITA[/bold]: Historial de chats ilimitado y persistente.

[dim]Tu arsenal de ciberseguridad, actualizado al máximo nivel.[/dim]
                """,
                title="[bold green]💎 RECOMENDADO[/bold green]",
                border_style="gold1",
                padding=(1, 2)
            ))
            console.print(f"[bold green]Precio Especial: ${SUBSCRIPTION_PRICE_USD:.0f} USD/mes (USDT)[/bold green]\n")
        
        console.rule(style="cyan")
        
        # Build menu options
        menu_idx = 1
        for i, pkg in enumerate(CREDIT_PACKAGES, 1):
            print_menu_option(str(menu_idx), f"💳 Comprar {pkg['name']}", f"{pkg['credits']} créditos - ${pkg['price']:.0f}")
            menu_idx += 1
        
        if not is_premium:
            print_menu_option(str(menu_idx), "👑 Comprar PREMIUM", f"{SUBSCRIPTION_BONUS_CREDITS} créditos/mes + herramientas - ${SUBSCRIPTION_PRICE_USD:.0f}/mes")
            premium_option = str(menu_idx)
            menu_idx += 1
        else:
            premium_option = None
        
        # Help option
        help_option = str(menu_idx)
        print_menu_option(help_option, "❓ ¿Cómo pagar?", "Información sobre el proceso de pago")
        
        print_menu_option("0", "Volver")
        console.rule(style="cyan")
        
        choice = get_input("Selecciona")
        
        if choice == "0":
            break
        
        # Show payment help
        if choice == help_option:
            show_payment_help()
            continue
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(CREDIT_PACKAGES):
                pkg = CREDIT_PACKAGES[choice_num - 1]
                console.print(f"\n[bold cyan]Generando factura para {pkg['credits']} créditos (${pkg['price']:.0f})...[/bold cyan]")
                with show_loading("Creando factura..."):
                    result = api_client.create_credits_invoice(amount=pkg['price'], credits=pkg['credits'])
                
                if result.get("success"):
                    url = result.get("invoice_url") or result.get("data", {}).get("invoice_url")
                    print_success("¡Factura creada!")
                    console.print(f"\n[bold]URL de pago:[/bold]\n{url}\n")
                    
                    if detector.open_url(url):
                        print_info("Navegador abierto.")
                    else:
                        print_info("Copia y abre la URL en tu navegador.")
                    
                    print_warning("Los créditos se añadirán automáticamente al completar el pago.")
                    input("\nPresiona Enter para continuar...")
                else:
                    print_error(result.get("error", "Error creando factura"))
                    input("\nPresiona Enter...")
            
            elif premium_option and choice == premium_option:
                # Buy Premium
                console.print(f"\n[bold magenta]Generando factura PREMIUM (${SUBSCRIPTION_PRICE_USD:.0f})...[/bold magenta]")
                with show_loading("Creando factura..."):
                    result = api_client.create_subscription_invoice()
                
                if result.get("success"):
                    url = result.get("invoice_url") or result.get("data", {}).get("invoice_url")
                    print_success("¡Factura creada!")
                    console.print(f"\n[bold]URL de pago:[/bold]\n{url}\n")
                    
                    if detector.open_url(url):
                        print_info("Navegador abierto.")
                    else:
                        print_info("Copia y abre la URL en tu navegador.")
                    
                    print_warning("Tu cuenta se actualizará automáticamente al completar el pago.")
                    input("\nPresiona Enter para continuar...")
                else:
                    print_error(result.get("error", "Error creando factura"))
                    input("\nPresiona Enter...")
        except ValueError:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════════════════════════

def main_menu():
    """Main application menu."""
    running = True
    
    while running:
        with show_loading("Cargando..."):
            status_result = api_client.get_status()
        
        if not status_result["success"]:
            print_error("Error de sesión. Por favor reinicia la aplicación.")
            break
        
        status = status_result["data"]
        sys_info = detector.get_system_info()
        
        clear_screen()
        
        mode = "OPERATIVO" if status.get("is_premium") else "CONSULTA"
        is_premium = status.get("is_premium", False)
        sub_status = status.get("subscription_status", "free").lower()
        
        # Logic to handle status display
        if is_premium:
            status_label = " PREMIUM "
            status_color = "bold white on green"
        else:
            if sub_status == "premium":
                # Paid but maybe expired or issue
                status_label = " PENDING / EXPIRED "
                status_color = "bold white on yellow"
            else:
                status_label = " FREE "
                status_color = "bold white on red"
        
        # Header
        # Header
        print_banner(show_skull=False)
        
        # 1. System Info (Centered & Compact)
        from rich.align import Align
        from rich.table import Table
        from rich.panel import Panel
        
        sys_info_text = f"[bold rgb(0,100,255)]OS:[/bold rgb(0,100,255)] {sys_info['distro']}  │  [bold rgb(0,100,255)]Shell:[/bold rgb(0,100,255)] {sys_info['shell']}  │  [bold rgb(0,100,255)]Root:[/bold rgb(0,100,255)] {sys_info['root']}"
        console.print(Align.center(Panel(sys_info_text, border_style="dim rgb(0,255,255)", padding=(0, 2), title="[dim]System[/dim]")))
        
        # 2. User Dashboard (Elegant Grid)
        # We use a table for alignment within a panel
        user_table = Table(show_header=False, box=None, padding=(0, 2))
        user_table.add_column("Key", style="bold rgb(0,255,255)", justify="right")
        user_table.add_column("Value", style="white")
        
        user_table.add_row("Identity 👤", status.get('username') or status.get('email'))
        user_table.add_row("Plan Status 💎", f"[{status_color}]{status_label}[/{status_color}]")
        user_table.add_row("Credits 💳", f"[bold]{status.get('credits', 0)}[/bold]")
        user_table.add_row("Mode ⚙️", mode)
        
        dashboard_panel = Panel(
            user_table,
            title="[bold rgb(0,255,255)] DOMINION DASHBOARD [/bold rgb(0,255,255)]",
            border_style="rgb(0,255,255)",
            padding=(1, 2)
        )
        console.print(dashboard_panel)
        console.print(Align.center("[dim]Modules: 🔍 Web Search  │  🤖 Agent Core[/dim]"))
        
        console.print() # spacer
        
        # Menu Options
        print_menu_option("1", "🧠 CONSOLA AI", "Consultas de seguridad con búsqueda web")
        if is_premium:
            print_menu_option("2", "🔧 HERRAMIENTAS", "Port Scanner y más (Premium)")
            print_menu_option("3", "🏪 TIENDA", "Créditos y suscripción")
            print_menu_option("4", "⚙️  CONFIGURACIÓN", "Cuenta y ajustes")
        else:
            print_menu_option("2", "🏪 TIENDA", "Obtener acceso Premium y Créditos")
            print_menu_option("3", "⚙️  CONFIGURACIÓN", "Cuenta y ajustes")
            
        print_menu_option("0", "🚪 SALIR")
        
        console.rule(style="dim rgb(0,255,255)")
        
        choice = get_input("Selecciona")
        
        if choice == "1":
            ai_console_mode()
                
        elif choice == "2":
            if is_premium:
                tools_menu()
            else:
                upgrade_menu()
            
        elif choice == "3":
            if is_premium:
                upgrade_menu()
            else:
                logged_out = config_menu()
                if logged_out:
                    break
        
        elif choice == "4" and is_premium:
            logged_out = config_menu()
            if logged_out:
                break
            
        elif choice == "0":
            if confirm("¿Salir de KaliRoot CLI?"):
                running = False
                print_success("¡Hasta pronto!")


def tools_menu():
    """Premium Tools Menu - Extended Suite."""
    from .tools.port_scanner import quick_scan, format_scan_results
    from .tools.repo_browser import RepoBrowser
    from .tools.cve_lookup import search_cve, format_cve_results
    from .tools.extra import gdrive_downloader, show_metasploit_resources
    
    browser = RepoBrowser()

    while True:
        clear_screen()
        print_banner(show_skull=False)
        
        # Original 3
        print_menu_option("1", "🔍 Port Scanner", "Escaneo rápido de puertos")
        print_menu_option("2", "💯 Top 100 Repositorios", "Repositorio de herramientas de Hacking")
        print_menu_option("3", "🛡️ CVE Lookup", "Busca vulnerabilidades")
        
        # New 10
        print_menu_option("4", "📥 GDrive Downloader", "Descargar archivos por ID")
        print_menu_option("5", "🧠 Hacking Labs", "HackTheBox, VulnHub & Scripts")
        print_menu_option("6", "🕵️ Digital Forensics", "Analisis Forense & Recuperación")
        print_menu_option("7", "⚡ Metasploit Resources", "Docs, Unleashed & Exploits")
        print_menu_option("8", "📱 Termux Utilities", "Herramientas para Android/Termux")
        print_menu_option("9", "🎭 Anonymity Tools", "Tor, Proxychains, VPNs")
        print_menu_option("10", "🦅 OSINT Dashboard", "Sherlock, Osintgram & More")
        print_menu_option("11", "📡 WiFi Auditing", "Aircrack-ng, Wifite, Fluxion")
        print_menu_option("12", "🔑 Password Cracking", "Hydra, John, Hashcat")
        print_menu_option("13", "🎣 Social Engineering", "Phishing & Engineering Tools")
        print_menu_option("14", "🎭 Fsociety Framework", "Pentesting modular completo")

        print_menu_option("0", "Volver")
        
        console.rule(style="dim rgb(0,255,255)")
        choice = get_input("Selecciona")
        
        if choice == "0":
            break
        
        elif choice == "1":
            # Port Scanner
            clear_screen()
            print_banner(show_skull=False)
            console.print("\n[bold cyan]═══ PORT SCANNER ═══[/bold cyan]\n")
            host = get_input("IP o Hostname a escanear")
            
            if not host:
                print_error("Debes ingresar un host.")
                continue
            
            with show_loading(f"Escaneando {host}..."):
                try:
                    results = quick_scan(host)
                    output = format_scan_results(host, results)
                except Exception as e:
                    output = f"Error: {e}"
            
            console.print(f"\n{output}\n")
            
            if results and confirm("¿Analizar resultados con AI?"):
                ports_info = ", ".join([f"{r['port']}/{r['service']}" for r in results])
                query = f"Analiza estos puertos abiertos en {host}: {ports_info}. Identifica posibles vulnerabilidades."
                
                with show_loading("Analizando con DOMINION..."):
                    analysis = api_client.ai_query(query, {})
                
                if analysis["success"]:
                     print_ai_response(analysis["data"]["response"])
            
            input("\nPresiona Enter para continuar...")

        elif choice == "2":
            browser.run() # Full browser
        
        elif choice == "3":
            # CVE Lookup
            clear_screen()
            print_banner(show_skull=False)
            console.print("\n[bold cyan]═══ CVE LOOKUP ═══[/bold cyan]\n")
            keyword = get_input("Buscar CVE (ej: apache, wordpress, ssh)")
            
            if keyword:
                with show_loading(f"Buscando CVEs para '{keyword}'..."):
                    results = search_cve(keyword, limit=5)
                    output = format_cve_results(results)
                
                console.print(f"\n{output}")
                
                if results and "error" not in results[0] and confirm("¿Analizar con AI?"):
                    cves = ", ".join([r["id"] for r in results])
                    query = f"Analiza estas vulnerabilidades: {cves}. ¿Cómo las explotaría un atacante?"
                    
                    with show_loading("Analizando con DOMINION..."):
                        analysis = api_client.ai_query(query, {})
                    
                    if analysis["success"]:
                        print_ai_response(analysis["data"]["response"])
            
            input("\nPresiona Enter para continuar...")

        elif choice == "4":
            gdrive_downloader()
        elif choice == "5":
            browser.browse_category("Labs")
        elif choice == "6":
            browser.browse_category("Forensics")
        elif choice == "7":
            show_metasploit_resources()
        elif choice == "8":
            browser.browse_category("Termux")
        elif choice == "9":
            browser.browse_category("Anonymity")
        elif choice == "10":
            browser.browse_category("OSINT")
        elif choice == "11":
            browser.browse_category("Wireless")
        elif choice == "12":
            browser.browse_category("Passwords")
        elif choice == "13":
            browser.browse_category("Social Eng")
        elif choice == "14":
            from .tools.fsociety_handler import run_fsociety_menu
            run_fsociety_menu()
            
            input("\nPresiona Enter para continuar...")


def ai_console_mode():
    """Interactive AI Console with persistent chat sessions."""
    from .chat_manager import ChatManager
    
    # Get username from status
    status_res = api_client.get_status()
    if not status_res["success"]:
        print_error("No se pudo obtener información de usuario.")
        return
    
    username = status_res["data"].get("username") or status_res["data"].get("email", "user")
    is_premium = status_res["data"].get("is_premium", False)
    chat_manager = ChatManager(username)
    
    # === CHAT SELECTION MENU ===
    while True:
        clear_screen()
        print_banner(show_skull=False)
        
        chats = chat_manager.list_chats()
        
        # Limit chats for Free users
        max_chats = 10 if is_premium else 5
        display_chats = chats[:max_chats]
        
        if chats:
            console.print("[bold cyan]Tus Chats:[/bold cyan]\n")
            for i, chat in enumerate(display_chats, 1):
                msg_count = chat["message_count"]
                updated = chat["updated_at"][:16].replace("T", " ")
                console.print(f" {i}. [bold]{chat['title']}[/bold]")
                console.print(f"    [dim]{msg_count} mensajes | Actualizado: {updated}[/dim]")
            
            if not is_premium and len(chats) > 5:
                console.print(f"\n[yellow]⭐ {len(chats) - 5} chats ocultos. Upgrade a Premium para ver todos.[/yellow]")
            console.print()
        else:
            console.print("[dim]No tienes chats aún. Crea uno nuevo para comenzar.[/dim]\n")
        
        print_menu_option("N", "Nuevo Chat", "Iniciar una conversación nueva")
        if chats:
            print_menu_option("1-10", "Abrir Chat", "Continuar una conversación existente")
            print_menu_option("D", "Eliminar Chat", "Borrar un chat")
            if is_premium:
                print_menu_option("E", "Exportar Chat", "Guardar como Markdown")
        print_menu_option("0", "Volver", "Regresar al menú principal")
        
        console.rule(style="rgb(0,255,255)")
        choice = get_input("Selecciona").strip().lower()
        
        if choice == "0":
            break
        elif choice == "n":
            title = get_input("Título del chat (Enter para auto)").strip()
            session = chat_manager.create_chat(title if title else None)
            run_chat_session(chat_manager, session)
        elif choice == "d" and chats:
            try:
                idx = int(get_input("Número de chat a eliminar")) - 1
                if 0 <= idx < len(chats):
                    chat_id = chats[idx]["chat_id"]
                    if confirm(f"¿Eliminar '{chats[idx]['title']}'?"):
                        chat_manager.delete_chat(chat_id)
                        print_success("Chat eliminado.")
                        input("\nPresiona Enter...")
            except ValueError:
                pass
        elif choice == "e" and is_premium and chats:
            # Export chat to Markdown
            try:
                idx = int(get_input("Número de chat a exportar")) - 1
                if 0 <= idx < len(display_chats):
                    chat = display_chats[idx]
                    session = chat_manager.load_chat(chat["chat_id"])
                    if session:
                        from datetime import datetime
                        filename = f"chat_{chat['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                        
                        with open(filename, "w") as f:
                            f.write(f"# {chat['title']}\n\n")
                            f.write(f"*Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n")
                            for msg in session.messages:
                                role = "**Usuario:**" if msg["role"] == "user" else "**DOMINION:**"
                                f.write(f"{role}\n{msg['content']}\n\n")
                        
                        print_success(f"Chat exportado a: {filename}")
                        input("\nPresiona Enter...")
            except ValueError:
                pass
        elif choice.isdigit() and chats:
            idx = int(choice) - 1
            if 0 <= idx < len(display_chats):
                session = chat_manager.load_chat(display_chats[idx]["chat_id"])
                if session:
                    run_chat_session(chat_manager, session)


def run_chat_session(chat_manager, session):
    """
    Run a continuous chat session.
    
    Args:
        chat_manager: ChatManager instance
        session: ChatSession to interact with
    """
    while True:
        clear_screen()
        # Elegant Chat Title
        from rich.align import Align
        from rich.panel import Panel
        console.print(Panel(
            Align.center(f"[bold white]💬 {session.title}[/bold white]"),
            border_style="rgb(0,255,255)",
            padding=(0, 2),
            expand=True
        ))
        
        # Display chat history
        if session.messages:
            console.print("[dim]─── Historial (últimos 8 mensajes) ───[/dim]\n")
            
            # Show last 8 messages with full content
            display_messages = session.messages[-8:]
            
            for msg in display_messages:
                role_style = "bold cyan" if msg["role"] == "user" else "bold magenta"
                role_label = "Tú" if msg["role"] == "user" else "KR-AI"
                
                # Display complete message with proper formatting
                from rich.panel import Panel
                from rich.markdown import Markdown
                
                # Try to render as markdown for better formatting
                try:
                    content = Markdown(msg['content'])
                except:
                    content = msg['content']
                
                # Use consistent border colors: User=Cyan, AI=Cyan
                border_color = "bright_cyan" if msg["role"] == "user" else "rgb(0,255,255)"
                
                console.print(Panel(
                    content,
                    title=f"[{role_style}]{role_label}[/{role_style}]",
                    border_style=border_color,
                    padding=(0, 1),
                    expand=False
                ))
        
        console.rule(style="rgb(0,255,255)")
        console.print("[dim]Escribe '/exit' para volver | '/clear' para limpiar historial[/dim]\n")
        
        # Get user input
        user_input = get_input("Tú").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["/exit", "/quit", "0"]:
            break
        
        if user_input.lower() == "/clear":
            if confirm("¿Limpiar todo el historial de este chat?"):
                session.messages = []
                chat_manager.save_chat(session)
                print_success("Historial limpiado.")
            continue
        
        # Add user message to session
        session.add_message("user", user_input)
        
        # Build context-aware prompt
        context = chat_manager.get_chat_context(session, max_messages=8)
        
        prompt = f"""
HISTORIAL DE CONVERSACIÓN:
{context}

Responde al último mensaje del usuario de forma natural y coherente con el contexto.
        """
        
        # Query AI
        with show_loading("KR-AI está pensando..."):
            env = detector.get_system_info()
            result = api_client.ai_query(prompt, env)
        
        if result["success"]:
            data = result["data"]
            ai_response = data.get("response", "")
            
            # Add AI response to session
            session.add_message("assistant", ai_response)
            
            # Save session
            chat_manager.save_chat(session)
            
            # Display response immediately with full content
            from rich.panel import Panel
            from rich.markdown import Markdown
            
            try:
                response_content = Markdown(ai_response)
            except:
                response_content = ai_response
            
            console.print()
            console.print(Panel(
                response_content,
                title="[bold magenta]KR-AI[/bold magenta]",
                border_style="rgb(0,255,255)",
                padding=(1, 2)
            ))
            console.print()
            
            if "credits_remaining" in data and data["credits_remaining"] is not None:
                console.print(f"[dim]💳 Créditos: {data['credits_remaining']}[/dim]\n")
        else:
            error_msg = result.get('error', 'Error desconocido')
            session.messages.pop()  # Remove user message if AI failed
            
            if "credits" in error_msg.lower() or "créditos" in error_msg.lower():
                # Get user status to check if premium
                status_res = api_client.get_status()
                is_user_premium = status_res.get("data", {}).get("is_premium", False) if status_res.get("success") else False
                
                clear_screen()
                console.print("\n[bold red]😔 ¡Se agotaron tus créditos![/bold red]\n")
                console.print("[bold white]Estábamos en algo importante...[/bold white]")
                console.print("[cyan]Tu última consulta era valiosa y DOMINION estaba[/cyan]")
                console.print("[cyan]listo para darte información exclusiva sobre el tema.[/cyan]\n")
                
                console.print("[bold yellow]🔥 No te quedes sin saber:[/bold yellow]")
                console.print("  • La respuesta completa está lista para ti")
                console.print("  • DOMINION tiene el conocimiento que buscas")
                console.print("  • Un solo paso te separa de continuar\n")
                
                console.rule(style="yellow")
                if is_user_premium:
                    console.print("[bold green]💎 Eres usuario PREMIUM[/bold green]")
                    print_menu_option("1", "💳 Comprar Créditos", "200 créditos - $10")
                else:
                    console.print("[bold green]💎 PAQUETES DISPONIBLES:[/bold green]")
                    console.print("  💳 [bold]Créditos[/bold]: 200 créditos - $10")
                    console.print("  👑 [bold]Premium[/bold]: 500 créditos + herramientas - $20/mes\n")
                    print_menu_option("1", "💎 Ver Tienda", "Comprar créditos o Premium")
                print_menu_option("0", "Volver al menú")
                console.rule(style="yellow")
                
                sub_choice = get_input("¿Qué deseas hacer?")
                if sub_choice == "1":
                    upgrade_menu()
                return  # Exit chat session
            else:
                print_error(error_msg)
                input("\nPresiona Enter para continuar...")



def config_menu():
    """Configuration menu. Returns True if user logged out."""
    while True:
        status_res = api_client.get_status()
        if not status_res["success"]:
            return False
            
        data = status_res["data"]
        
        clear_screen()
        print_banner(show_skull=False)
        console.print(f"👤 Usuario: {data.get('username')}")
        console.print(f"📧 Email: {data.get('email')}")
        console.print(f"🆔 User ID: {data.get('user_id')}")
        console.print(f"💳 Créditos: {data.get('credits')}")
        console.print(f"📅 Suscripción: {data.get('subscription_status')}")
        console.print("\n")
        
        print_menu_option("1", "Cerrar Sesión")
        print_menu_option("0", "Volver")
        
        choice = get_input("Opción")
        
        if choice == "1":
            if confirm("¿Cerrar sesión?"):
                api_client.logout()
                console.print("\n[bold cyan]👋 ¡Hasta pronto! Sesión cerrada correctamente.[/bold cyan]")
                console.print("[dim]Gracias por usar KR-CLI DOMINION. Protegiendo tu entorno...[/dim]\n")
                import time
                time.sleep(2)
                return True  # Return True to signal logout
        elif choice == "0":
            return False  # Return False for normal exit



def settings_menu() -> bool:
    """Settings menu. Returns True if should exit app."""
    print_banner(show_skull=False)
    
    sys_info = detector.get_system_info()
    
    console.print(f"[bold]Sistema:[/bold] {detector.get_distro_name()}")
    console.print(f"[bold]Usuario:[/bold] {api_client.email or 'Invitado'}")
    console.print(f"[bold]Shell:[/bold] {sys_info['shell']}")
    
    # Module status
    console.print(f"\n[bold]Estado de módulos:[/bold]")
    console.print(f"  🔍 Búsqueda Web: {'[green]Disponible[/green]' if WEB_SEARCH_AVAILABLE else '[red]No disponible[/red]'}")
    console.print(f"  🤖 Agente: {'[green]Disponible[/green]' if AGENT_AVAILABLE else '[red]No disponible[/red]'}")
    
    if AGENT_AVAILABLE:
        console.print(f"\n[bold]Directorio de proyectos:[/bold]")
        console.print(f"  [dim]{file_agent.base_dir}[/dim]")
    
    print_divider()
    print_menu_option("1", "🚪 Cerrar Sesión")
    print_menu_option("0", "⬅️  Volver")
    
    choice = get_input("Selecciona")
    
    if choice == "1":
        if confirm("¿Cerrar sesión?"):
            api_client.logout()
            print_success("Sesión cerrada.")
            return True
    
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Application entry point."""
    try:
        # Import animated splash
        try:
            from .ui.splash import animated_splash
            SPLASH_AVAILABLE = True
        except ImportError:
            SPLASH_AVAILABLE = False
        
        # Check for --no-splash or -q flag
        skip_splash = "--no-splash" in sys.argv or "-q" in sys.argv
        
        # Animated splash screen (5 second cinematic intro)
        if SPLASH_AVAILABLE and not skip_splash:
            animated_splash(skip_animation=False, duration=5.0)
        
        # Clear and show main banner
        clear_screen()
        print_banner()
        
        # System info
        sys_info = detector.get_system_info()
        print_info(f"Sistema: {sys_info['distro']} │ {sys_info['shell']}")
        
        # Show module status
        modules = []
        if WEB_SEARCH_AVAILABLE:
            modules.append("🔍 Web Search")
        if AGENT_AVAILABLE:
            modules.append("🤖 Agent")
        
        if modules:
            print_info(f"Módulos: {' │ '.join(modules)}")
        
        # Authenticate
        if not authenticate():
            console.print("\n[cyan]¡Hasta pronto![/cyan]\n")
            sys.exit(0)
        
        # Main menu
        main_menu()
        
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Interrumpido.[/bold cyan]\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {e}")
        logger.exception("Main crash")
        sys.exit(1)


if __name__ == "__main__":
    main()


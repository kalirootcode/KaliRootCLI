"""
Main entry point for KaliRoot CLI
Professional Cybersecurity CLI with AI, Web Search, and Agent Capabilities.

Version: 2.0.0
"""

import sys
import logging
from getpass import getpass
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
    print_panel
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
        console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]           AUTENTICACIÓN KR-CLI          [/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
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
                return True
            else:
                error = result.get("error", "Error de autenticación")
                print_error(error)
                
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
        
        console.clear()
        
        mode = "OPERATIVO" if status["is_premium"] else "CONSULTA"
        color = "green" if status["is_premium"] else "yellow"
        
        # Header
        console.print(f"\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
        console.print(f"[bold cyan]                    🔒 KALIROOT CLI v2.0                        [/bold cyan]")
        console.print(f"[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
        
        # System info
        console.print(f"\n[dim]{sys_info['distro']} │ {sys_info['shell']} │ Root: {sys_info['root']}[/dim]")
        
        # User status
        console.print(f"\n[bold]👤 Usuario:[/bold] {status['username']}")
        console.print(f"[bold]⚙️  Modo:[/bold] [{color}]{mode}[/{color}]")
        console.print(f"[bold]💳 Créditos:[/bold] {status['credits']}")
        
        if status["is_premium"]:
            console.print(f"[bold]⭐ Premium:[/bold] [green]{status['days_left']} días restantes[/green]")
        
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
        print_menu_option("2", "🤖 MODO AGENTE", "Crear archivos, proyectos y planes")
        print_menu_option("3", "📋 PLANIFICADOR", "Gestión de proyectos y auditorías")
        print_menu_option("4", "⭐ UPGRADE", "Obtener acceso Premium")
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
            print_error(result["error"])
            if "credits" in result["error"].lower() or "créditos" in result["error"].lower():
                break


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

def agent_menu():
    """Agent mode for file and project creation."""
    if not AGENT_AVAILABLE:
        print_error("El módulo de agente no está disponible. Instala las dependencias.")
        get_input("Presiona Enter para continuar...")
        return
    
    while True:
        print_header("🤖 MODO AGENTE")
        
        console.print("[dim]Crea archivos, proyectos y código automáticamente.[/dim]\n")
        
        print_menu_option("1", "📄 Crear Script", "Python o Bash desde plantilla")
        print_menu_option("2", "📁 Crear Proyecto", "Estructura completa de proyecto")
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


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

def planner_menu():
    """Project planning menu."""
    if not AGENT_AVAILABLE:
        print_error("El módulo de planificación no está disponible.")
        get_input("Presiona Enter para continuar...")
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


# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE & SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

def upgrade_menu():
    """Handle premium upgrade."""
    print_header("⭐ UPGRADE A PREMIUM")
    
    console.print("""
[bold green]BENEFICIOS PREMIUM:[/bold green]

  ✅ Consultas AI ilimitadas
  ✅ Generación completa de scripts
  ✅ Análisis de vulnerabilidades avanzado
  ✅ +250 créditos bonus/mes
  ✅ Búsqueda web enriquecida
  ✅ Soporte prioritario

[bold]Precio: $10/mes (USDT)[/bold]
""")
    
    if confirm("¿Crear factura de pago?"):
        with show_loading("Generando factura..."):
            result = api_client.create_subscription_invoice()
        
        if result["success"]:
            url = result["data"]["invoice_url"]
            print_success("¡Factura creada!")
            console.print(f"\n[bold]URL de pago:[/bold]\n{url}\n")
            
            if detector.open_url(url):
                print_info("Navegador abierto.")
            else:
                print_info("Copia y abre la URL en tu navegador.")
                
            console.print("[dim]Después del pago, tu cuenta se actualizará automáticamente.[/dim]")
        else:
            print_error(result["error"])
    
    get_input("\nPresiona Enter para continuar...")


def settings_menu() -> bool:
    """Settings menu. Returns True if should exit app."""
    print_header("⚙️ CONFIGURACIÓN")
    
    sys_info = detector.get_system_info()
    
    console.print(f"[bold]Sistema:[/bold] {detector.get_distro_name()}")
    console.print(f"[bold]Usuario:[/bold] {api_client.username}")
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
        console.clear()
        print_banner()
        
        # Detect environment
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


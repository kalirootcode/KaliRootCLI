"""
Menu system for KaliRoot CLI — DOMINION Edition
Professional interactive dashboards unified under the DOMINION tier.
No Free/Premium distinction — access governed by KR balance.
"""

from rich.table import Table
from rich import box
from rich.panel import Panel

from .display import (
    console,
    print_header,
    print_menu_option,
    print_divider,
    print_error,
    print_success,
    print_panel,
    print_ai_response,
    get_input,
    confirm,
    show_loading,
    print_info,
    clear_and_show_banner,
)


class MainMenu:
    """Professional DOMINION Main Dashboard."""

    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self._running = True

    def show(self) -> None:
        """Show and handle main dashboard."""
        from .economy import EconomyManager
        from .ai_handler import AIHandler
        from .distro_detector import detector

        eco = EconomyManager(self.user_id)

        while self._running:
            eco.refresh()
            self._render_dashboard(eco, detector)

            choice = get_input("Selecciona una Opción")

            if choice == "1":
                self._ai_interface(eco)
            elif choice == "2":
                self._agent_interface(eco)
            elif choice == "3":
                self._project_manager(eco)
            elif choice == "4":
                self._show_wallet(eco)
            elif choice == "5":
                self._recharge_menu(eco)
            elif choice == "6":
                self._show_profile()
            elif choice == "7":
                self._settings_menu()
            elif choice == "8":
                self._show_help()
            elif choice == "0":
                if confirm("¿Salir de KaliRoot CLI DOMINION?"):
                    self._running = False
                    console.print(
                        "\n[bold cyan]👋 Sesión DOMINION Terminada. Stay elite.[/bold cyan]\n"
                    )
            else:
                print_error("Opción inválida")

    # ─── Dashboard Render ─────────────────────────────────────────────────────

    def _render_dashboard(self, eco, detector) -> None:
        """Render the DOMINION main dashboard."""
        clear_and_show_banner()

        # Top status bar
        grid = Table.grid(expand=True)
        grid.add_column(justify="left",  ratio=1)
        grid.add_column(justify="right", ratio=1)

        grid.add_row(
            f"[bold rgb(0,100,255)]👤 USUARIO:[/bold rgb(0,100,255)] {self.username.upper()}",
            f"[bold cyan]⚡ Billetera KR: {eco.kr_balance} KR[/bold cyan]",
        )

        console.print(Panel(grid, style="rgb(0,255,255)", box=box.HEAVY))

        # System context line
        sys_info = detector.get_system_info()
        console.print(
            f"[dim]SISTEMA: {sys_info['distro']} | SHELL: {sys_info['shell']} "
            f"| ROOT: {sys_info['root']} | TIER: DOMINION[/dim]"
        )
        print_divider()

        # Menu options — professional, direct naming
        print_menu_option("1", "CONSULTORÍA IA",          "Preguntas técnicas, análisis y scripting  [-1 KR]")
        print_menu_option("2", "AGENTE DE AUTOMATIZACIÓN","Creación autónoma de proyectos y archivos [-5 KR]")
        print_menu_option("3", "GESTOR DE PROYECTOS",     "Administra tus proyectos activos")
        print_menu_option("4", "BILLETERA KR",            f"Saldo actual: {eco.kr_balance} KR")
        print_menu_option("5", "RECARGAR KR",             "Adquiere paquetes de créditos KR")
        print_menu_option("6", "PERFIL",                  "Detalles de cuenta e historial")
        print_menu_option("7", "CONFIGURACIÓN",           "Ajustes del sistema")
        print_menu_option("8", "MANUAL",                  "Ayuda y documentación DOMINION")
        print_menu_option("0", "SALIR",                   "Terminar sesión")

        print_divider()

    # ─── Option 1: AI Consultation ────────────────────────────────────────────

    def _ai_interface(self, eco) -> None:
        """DOMINION AI Interface — all capabilities, KR gated."""
        from .ai_handler import AIHandler
        from .economy import show_zero_balance_panel, show_kr_spend_panel
        from .config import KR_COST_CHAT

        clear_and_show_banner()
        print_header("CONSULTORÍA IA — DOMINION")

        console.print(Panel(
            "[bold cyan]⚡ DOMINION AI ACTIVO[/bold cyan]  ·  Capacidades completas habilitadas\n"
            "[dim]Escribe 'salir' para volver al dashboard.[/dim]",
            border_style="rgb(0,200,180)",
            padding=(0, 2),
        ))

        ai_handler = AIHandler(self.user_id)

        while True:
            eco.refresh()

            query = get_input(f"CMD/QUERY [{eco.kr_balance} KR]")

            if query.lower() in ["exit", "quit", "salir", "back"]:
                break

            if not query:
                continue

            # KR balance check
            if not eco.has_balance(KR_COST_CHAT):
                show_zero_balance_panel()
                get_input("Presiona Enter para continuar...")
                break

            show_kr_spend_panel(KR_COST_CHAT, "Consultoría IA")

            with show_loading("Analizando solicitud con DOMINION AI..."):
                response = ai_handler.get_response(query)

            print_ai_response(response, "OPERATIONAL")
            eco.refresh()
            console.print(f"[dim]⚡ KR restantes: {eco.kr_balance}[/dim]\n")

    # ─── Option 2: Agent ──────────────────────────────────────────────────────

    def _agent_interface(self, eco) -> None:
        """Automation Agent interface — KR gated."""
        from .economy import show_zero_balance_panel, show_kr_spend_panel
        from .config import KR_COST_AGENT

        clear_and_show_banner()
        print_header("AGENTE DE AUTOMATIZACIÓN — DOMINION")

        eco.refresh()
        if not eco.has_balance(KR_COST_AGENT):
            show_zero_balance_panel()
            get_input("Presiona Enter...")
            return

        console.print(Panel(
            "[bold cyan]⚡ Agente de Automatización DOMINION[/bold cyan]\n"
            "[dim]Describe la tarea que el Agente debe ejecutar.[/dim]\n"
            "[dim]Escribe 'salir' para volver al dashboard.[/dim]",
            border_style="rgb(0,200,180)",
            padding=(0, 2),
        ))

        try:
            from .agent import AgentFileManager
            from .ai_handler import AIHandler

            manager = AgentFileManager()
            ai_handler = AIHandler(self.user_id)

            while True:
                eco.refresh()
                task = get_input(f"TAREA DEL AGENTE [{eco.kr_balance} KR]")

                if task.lower() in ["exit", "quit", "salir", "back"]:
                    break
                if not task:
                    continue

                if not eco.has_balance(KR_COST_AGENT):
                    show_zero_balance_panel()
                    break

                show_kr_spend_panel(KR_COST_AGENT, "Agente de Automatización")

                with show_loading("🤖 Agente ejecutando tarea..."):
                    result = manager.run_task(task)

                if result.get("success"):
                    print_success(f"✅ Tarea completada: {result.get('message', '')}")
                else:
                    print_error(f"❌ Error en la tarea: {result.get('error', 'Error desconocido')}")

                eco.refresh()
                console.print(f"[dim]⚡ KR restantes: {eco.kr_balance}[/dim]\n")

        except ImportError as e:
            print_error(f"Error cargando el módulo de agente: {e}")
            get_input("Presiona Enter...")

    # ─── Option 3: Project Manager ────────────────────────────────────────────

    def _project_manager(self, eco) -> None:
        """Project manager menu."""
        clear_and_show_banner()
        print_header("GESTOR DE PROYECTOS — DOMINION")

        try:
            from .agent import AgentFileManager
            from .config import KR_COST_AGENT
            from .economy import show_zero_balance_panel, show_kr_spend_panel

            manager = AgentFileManager()

            console.print(Panel(
                "[dim]Crea y gestiona estructuras de proyectos de seguridad.[/dim]",
                border_style="rgb(0,200,180)",
            ))

            print_menu_option("1", "Nuevo Proyecto",    "Crear estructura de proyecto")
            print_menu_option("0", "Volver",            "Regresar al dashboard")
            print_divider()

            choice = get_input("Selecciona")

            if choice == "1":
                eco.refresh()
                if not eco.has_balance(KR_COST_AGENT):
                    show_zero_balance_panel()
                    get_input("Presiona Enter...")
                    return

                name = get_input("Nombre del proyecto")
                if not name:
                    print_error("Nombre requerido.")
                    return

                proj_type = get_input("Tipo (pentest/tool/audit/research/ctf/scanner_tool)")
                if not proj_type:
                    proj_type = "pentest"

                show_kr_spend_panel(KR_COST_AGENT, "Gestor de Proyectos")

                with show_loading("Creando estructura del proyecto..."):
                    from .agent import PROJECT_STRUCTURES
                    if proj_type not in PROJECT_STRUCTURES:
                        proj_type = "pentest"

                    project_path = manager.get_project_path()
                    import os
                    from pathlib import Path
                    proj_dir = Path(project_path) / name
                    proj_dir.mkdir(parents=True, exist_ok=True)

                    structure = PROJECT_STRUCTURES[proj_type]
                    for d in structure.get("dirs", []):
                        (proj_dir / d).mkdir(parents=True, exist_ok=True)
                    for fname, content in structure.get("files", {}).items():
                        fpath = proj_dir / fname
                        fpath.parent.mkdir(parents=True, exist_ok=True)
                        fpath.write_text(content.replace("{name}", name))

                print_success(f"✅ Proyecto '{name}' creado en: {proj_dir}")
                eco.refresh()
                console.print(f"[dim]⚡ KR restantes: {eco.kr_balance}[/dim]")

        except Exception as e:
            print_error(f"Error en gestor de proyectos: {e}")

        get_input("Presiona Enter...")

    # ─── Option 4: Wallet ─────────────────────────────────────────────────────

    def _show_wallet(self, eco) -> None:
        """Show KR wallet status."""
        clear_and_show_banner()
        print_header("BILLETERA KR — DOMINION")

        eco.refresh()

        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Campo",  style="rgb(0,255,200)", width=20)
        table.add_column("Valor",  style="bold white")

        table.add_row("⚡ Saldo KR",     str(eco.kr_balance))
        table.add_row("🏆 Tier",         "DOMINION")
        table.add_row("💬 Chat (-KR)",    "1 KR por consulta")
        table.add_row("🤖 Agente (-KR)", "5 KR por acción")
        table.add_row("📄 Reporte (-KR)","10 KR por reporte")

        console.print(table)
        get_input("Presiona Enter...")

    # ─── Option 5: Recharge ───────────────────────────────────────────────────

    def _recharge_menu(self, eco) -> None:
        """KR recharge packages."""
        from .economy import get_kr_packages_display
        from .config import KR_PACKAGES

        clear_and_show_banner()
        print_header("RECARGAR KR — DOMINION")

        console.print(get_kr_packages_display())

        choice = get_input("Selecciona Paquete # (0 para cancelar)")
        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(KR_PACKAGES):
                eco.start_kr_recharge_flow(idx)
                get_input("Presiona Enter una vez completado el pago...")
                eco.refresh()
                print_success(f"✅ Saldo actualizado: {eco.kr_balance} KR")
            else:
                print_error("Paquete inválido")
        except ValueError:
            print_error("Entrada inválida")

    # ─── Option 6: Profile ────────────────────────────────────────────────────

    def _show_profile(self) -> None:
        """Show user profile."""
        from .database_manager import get_user_profile

        clear_and_show_banner()
        print_header("PERFIL DE USUARIO — DOMINION")

        profile = get_user_profile(self.user_id)

        if profile:
            console.print(Panel(
                f"""
[bold]Username:[/bold]  {profile['username']}
[bold]ID:[/bold]        {profile['id']}
[bold]Tier:[/bold]      [bold cyan]DOMINION[/bold cyan]
[bold]Creado:[/bold]    {profile['created_at']}
                """,
                title="[bold cyan]Detalles de Cuenta[/bold cyan]",
                border_style="rgb(0,255,255)",
            ))
        get_input("Presiona Enter...")

    # ─── Option 7: Settings ───────────────────────────────────────────────────

    def _settings_menu(self) -> None:
        """Settings menu."""
        from .auth import auth_manager
        from .distro_detector import detector

        clear_and_show_banner()
        print_header("CONFIGURACIÓN DEL SISTEMA")

        sys_info = detector.get_system_info()
        console.print(Panel(
            f"""
[bold]Distro:[/bold]      {sys_info['distro']}
[bold]Gestor Pkg:[/bold]  {sys_info['pkg_manager']}
[bold]Directorio:[/bold]  {detector.get_data_dir()}
            """,
            title="[bold cyan]Entorno[/bold cyan]",
            border_style="rgb(0,255,255)",
        ))

        if confirm("¿Cerrar sesión en este dispositivo?"):
            auth_manager.logout()
            self._running = False
            print_success("Sesión cerrada correctamente.")

    # ─── Option 8: Help ───────────────────────────────────────────────────────

    def _show_help(self) -> None:
        """DOMINION manual."""
        clear_and_show_banner()
        print_header("MANUAL OPERATIVO — DOMINION")

        console.print("""
[bold rgb(0,255,200)]⚡ MODO DOMINION[/bold rgb(0,255,200)]
Todos los usuarios tienen acceso completo. El acceso se rige por KR balance.

[bold cyan]1. Consultoría IA  (-1 KR/consulta)[/bold cyan]
   • Consultas técnicas de ciberseguridad
   • Generación de scripts y payloads
   • Análisis de vulnerabilidades
   • Soporte completo de herramientas (Metasploit, Burp, SQLmap, etc.)

[bold cyan]2. Agente de Automatización  (-5 KR/acción)[/bold cyan]
   • Creación autónoma de archivos y proyectos
   • Scaffolding de pentest, CTF, audit, research
   • Agente OODA con ejecución de comandos

[bold cyan]3. Gestor de Proyectos  (-5 KR/creación)[/bold cyan]
   • Estructuras profesionales de proyectos de seguridad

[bold cyan]📄 Reportes Ejecutivos  (-10 KR/reporte)[/bold cyan]
   • Análisis de sesión y generación de PDF profesional

[bold rgb(0,255,65)]💚 Recarga KR[/bold rgb(0,255,65)]
   kalirootcode.github.io/KaliRootCLI/links.html

[dim]⚠️  Todas las acciones son para uso profesional autorizado.[/dim]
        """)
        get_input("Presiona Enter...")

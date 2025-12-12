"""
Menu system for KaliRoot CLI
Handles all interactive menus.
"""

from typing import Optional, Callable
from rich.table import Table
from rich import box

from .display import (
    console, 
    print_header, 
    print_menu_option,
    print_divider,
    print_error,
    print_success,
    print_warning,
    print_info,
    print_ai_response,
    get_input,
    confirm,
    clear_screen,
    print_panel,
    show_loading
)


class MainMenu:
    """Main menu handler."""
    
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self._running = True
    
    def show(self) -> None:
        """Show and handle main menu."""
        from ..subscription import SubscriptionManager, get_plan_comparison, get_credits_packages_display
        from ..ai_handler import get_ai_response
        from ..distro_detector import detector
        from ..database_manager import get_user_profile
        from ..config import CREDIT_PACKAGES
        
        sub_manager = SubscriptionManager(self.user_id)
        
        while self._running:
            # Get fresh status
            sub_manager.refresh()
            status = sub_manager.get_status_display()
            
            # Show menu
            console.print("\n")
            console.print(f"[bold cyan]╔{'═' * 48}╗[/bold cyan]")
            console.print(f"[bold cyan]║[/bold cyan]{'KALIROOT CLI':^48}[bold cyan]║[/bold cyan]")
            console.print(f"[bold cyan]║[/bold cyan]{detector.get_distro_emoji()} {detector.get_distro_name():^45}[bold cyan]║[/bold cyan]")
            console.print(f"[bold cyan]╠{'═' * 48}╣[/bold cyan]")
            console.print(f"[bold cyan]║[/bold cyan] 👤 [white]{self.username}[/white]")
            console.print(f"[bold cyan]║[/bold cyan] {status}")
            console.print(f"[bold cyan]╠{'═' * 48}╣[/bold cyan]")
            
            print_menu_option("1", "Consultar IA", "🤖")
            print_menu_option("2", "Mi Saldo", "💰")
            print_menu_option("3", "Suscripción Premium", "💎")
            print_menu_option("4", "Comprar Créditos", "🛒")
            print_menu_option("5", "Mi Perfil", "👤")
            print_menu_option("6", "Configuración", "⚙️")
            print_menu_option("7", "Ayuda", "❓")
            print_menu_option("0", "Salir", "🚪")
            
            console.print(f"[bold cyan]╚{'═' * 48}╝[/bold cyan]")
            
            choice = get_input("\nOpción: ")
            
            if choice == "1":
                self._ai_chat(sub_manager)
            elif choice == "2":
                self._show_balance(sub_manager)
            elif choice == "3":
                self._subscription_menu(sub_manager)
            elif choice == "4":
                self._credits_menu(sub_manager)
            elif choice == "5":
                self._show_profile()
            elif choice == "6":
                self._settings_menu()
            elif choice == "7":
                self._show_help()
            elif choice == "0":
                if confirm("¿Seguro que quieres salir?"):
                    self._running = False
                    console.print("\n[cyan]👋 ¡Hasta pronto, hacker![/cyan]\n")
            else:
                print_error("Opción no válida")
    
    def _ai_chat(self, sub_manager) -> None:
        """AI chat mode."""
        from ..ai_handler import get_ai_response
        
        print_header("ASISTENTE IA KALIROOT")
        
        if sub_manager.is_premium:
            console.print("[green]👑 Modo Premium: Consultas ilimitadas[/green]\n")
        else:
            console.print(f"[yellow]💰 Créditos disponibles: {sub_manager.credits}[/yellow]\n")
        
        console.print("[dim]Escribe tu pregunta. Usa 'salir' para volver al menú.[/dim]\n")
        
        while True:
            query = get_input("🔍 ")
            
            if query.lower() in ['salir', 'exit', 'q', 'quit']:
                break
            
            if not query:
                continue
            
            with show_loading("Pensando..."):
                response = get_ai_response(self.user_id, query)
            
            print_ai_response(response)
            
            # Refresh credits after query
            sub_manager.refresh()
            
            if not sub_manager.is_premium:
                console.print(f"[dim]Créditos restantes: {sub_manager.credits}[/dim]\n")
    
    def _show_balance(self, sub_manager) -> None:
        """Show balance and subscription info."""
        print_header("MI SALDO")
        
        details = sub_manager.get_subscription_details()
        
        table = Table(box=box.ROUNDED, show_header=False)
        table.add_column("", style="cyan")
        table.add_column("", style="white")
        
        table.add_row("💰 Créditos", str(details["credits"]))
        table.add_row("📋 Estado", "Premium 💎" if details["is_premium"] else "Free")
        
        if details["is_premium"]:
            table.add_row("📅 Días restantes", str(details["days_left"]))
        
        console.print(table)
        console.print("")
        
        get_input("Presiona Enter para continuar...")
    
    def _subscription_menu(self, sub_manager) -> None:
        """Subscription menu."""
        from ..subscription import get_plan_comparison
        
        print_header("SUSCRIPCIÓN PREMIUM")
        
        if sub_manager.is_premium:
            console.print("[green]✅ Ya eres usuario Premium![/green]\n")
            details = sub_manager.get_subscription_details()
            console.print(f"📅 Tu suscripción expira en [cyan]{details['days_left']}[/cyan] días.\n")
            get_input("Presiona Enter para continuar...")
            return
        
        # Show plan comparison
        console.print(get_plan_comparison())
        
        console.print("\n[bold]¿Deseas activar Premium?[/bold]\n")
        print_menu_option("1", "Sí, activar Premium ($10/mes)")
        print_menu_option("0", "Volver")
        
        choice = get_input("\nOpción: ")
        
        if choice == "1":
            sub_manager.start_subscription_flow()
            console.print("\n[yellow]Una vez completado el pago, tu suscripción se activará automáticamente.[/yellow]")
            console.print("[dim]Esto puede tomar unos minutos.[/dim]\n")
            get_input("Presiona Enter para continuar...")
    
    def _credits_menu(self, sub_manager) -> None:
        """Credits purchase menu."""
        from ..subscription import get_credits_packages_display
        from ..config import CREDIT_PACKAGES
        
        print_header("COMPRAR CRÉDITOS")
        
        console.print(f"[dim]Saldo actual: {sub_manager.credits} créditos[/dim]\n")
        
        # Show packages
        console.print(get_credits_packages_display())
        
        console.print("\n[bold]Selecciona un paquete:[/bold]")
        for i in range(len(CREDIT_PACKAGES)):
            print_menu_option(str(i + 1), CREDIT_PACKAGES[i]["name"])
        print_menu_option("0", "Volver")
        
        choice = get_input("\nOpción: ")
        
        if choice == "0":
            return
        
        try:
            pkg_index = int(choice) - 1
            if 0 <= pkg_index < len(CREDIT_PACKAGES):
                sub_manager.start_credits_flow(pkg_index)
                console.print("\n[yellow]Una vez completado el pago, los créditos se añadirán automáticamente.[/yellow]\n")
                get_input("Presiona Enter para continuar...")
            else:
                print_error("Opción no válida")
        except ValueError:
            print_error("Opción no válida")
    
    def _show_profile(self) -> None:
        """Show user profile."""
        from ..database_manager import get_user_profile, get_subscription_info
        
        print_header("MI PERFIL")
        
        profile = get_user_profile(self.user_id)
        sub_info = get_subscription_info(self.user_id)
        
        if profile:
            table = Table(box=box.ROUNDED, show_header=False)
            table.add_column("", style="cyan", width=20)
            table.add_column("", style="white")
            
            table.add_row("👤 Username", profile.get("username", "N/A"))
            table.add_row("🆔 ID", str(profile.get("id", "N/A"))[:8] + "...")
            table.add_row("💰 Créditos", str(profile.get("credit_balance", 0)))
            
            if sub_info:
                status = "Premium 💎" if sub_info.get("is_active") else "Free"
                table.add_row("📋 Estado", status)
                
                if sub_info.get("is_active"):
                    table.add_row("📅 Expira en", f"{sub_info.get('days_left', 0)} días")
            
            table.add_row("📆 Registrado", str(profile.get("created_at", "N/A"))[:10])
            
            console.print(table)
        else:
            print_error("No se pudo cargar el perfil")
        
        console.print("")
        get_input("Presiona Enter para continuar...")
    
    def _settings_menu(self) -> None:
        """Settings menu."""
        from ..auth import auth_manager
        from ..distro_detector import detector
        from ..config import get_config_status
        
        print_header("CONFIGURACIÓN")
        
        # Show system info
        info = detector.get_system_info()
        config_status = get_config_status()
        
        table = Table(title="Sistema", box=box.ROUNDED, show_header=False)
        table.add_column("", style="cyan")
        table.add_column("", style="white")
        
        table.add_row("🖥️ Distribución", detector.get_distro_name())
        table.add_row("🐍 Python", info.get("python", "N/A"))
        table.add_row("💾 Datos", detector.get_data_dir())
        
        console.print(table)
        console.print("")
        
        # Config status
        table2 = Table(title="Servicios", box=box.ROUNDED, show_header=False)
        table2.add_column("", style="cyan")
        table2.add_column("", style="white")
        
        table2.add_row("🗄️ Supabase", "✅ Conectado" if config_status["supabase"] else "❌ No configurado")
        table2.add_row("🤖 Groq AI", "✅ Activo" if config_status["groq"] else "❌ No configurado")
        table2.add_row("💳 Pagos", "✅ Activo" if config_status["payments"] else "❌ No configurado")
        
        console.print(table2)
        console.print("")
        
        print_menu_option("1", "Cerrar sesión", "🚪")
        print_menu_option("0", "Volver")
        
        choice = get_input("\nOpción: ")
        
        if choice == "1":
            if confirm("¿Cerrar sesión?"):
                auth_manager.logout()
                console.print("[green]Sesión cerrada exitosamente.[/green]")
                self._running = False
    
    def _show_help(self) -> None:
        """Show help information."""
        print_header("AYUDA")
        
        help_text = """
[bold cyan]🤖 Consultar IA[/bold cyan]
Accede al asistente de IA especializado en ciberseguridad.
Pregunta sobre hacking, pentesting, Kali Linux, Termux y más.

[bold cyan]💰 Créditos[/bold cyan]
Cada consulta de IA consume 1 crédito (usuarios Free).
Los usuarios Premium tienen consultas ilimitadas.

[bold cyan]💎 Premium[/bold cyan]
Por $10/mes obtienes:
• Consultas ilimitadas
• +250 créditos bonus mensuales
• Soporte prioritario

[bold cyan]🛒 Comprar Créditos[/bold cyan]
Puedes comprar paquetes de créditos con criptomonedas (USDT).

[bold cyan]⚙️ Comandos rápidos[/bold cyan]
• Escribe 'ia' o 'ai' para ir directo al chat
• Escribe 'salir' o 'q' para salir de cualquier sección

[bold cyan]📞 Soporte[/bold cyan]
Contacta en Telegram: @KaliRootHack
"""
        console.print(help_text)
        get_input("\nPresiona Enter para continuar...")

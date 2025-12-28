"""
Menu system for KaliRoot CLI
Professional interactive dashboards.
"""

from rich.table import Table
from rich import box
from rich.layout import Layout
from rich.console import Console
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
    clear_and_show_banner
)

class MainMenu:
    """Professional Main Dashboard."""
    
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self._running = True
    
    def show(self) -> None:
        """Show and handle main dashboard."""
        from ..subscription import SubscriptionManager, get_plan_comparison
        from ..ai_handler import AIHandler
        from ..distro_detector import detector
        
        sub_manager = SubscriptionManager(self.user_id)
        
        while self._running:
            # Refresh context
            sub_manager.refresh()
            ai_handler = AIHandler(self.user_id)
            mode = ai_handler.get_mode()
            
            self._render_dashboard(sub_manager, mode, detector)
            
            choice = get_input("Select Option")
            
            if choice == "1":
                self._ai_interface(sub_manager, ai_handler)
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
                if confirm("Exit KaliRoot CLI?"):
                    self._running = False
                    console.print("\n[bold yellow]👋 Session Terminated.[/bold yellow]\n")
            else:
                print_error("Invalid option")

    def _render_dashboard(self, sub_manager, mode, detector):
        """Render the main professional dashboard."""
        clear_and_show_banner()
        
        # Top Status Bar
        status_color = "green" if sub_manager.is_premium else "yellow"
        mode_str = mode.value.upper()
        
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        grid.add_row(
            f"[bold rgb(0,100,255)]👤 USER:[/bold rgb(0,100,255)] {self.username.upper()}",
            f"[bold {status_color}]● {mode_str} MODE[/bold {status_color}]"
        )
        
        # Changed style from "blue" to "rgb(0,255,255)"
        console.print(Panel(grid, style="rgb(0,255,255)", box=box.HEAVY))
        
        # System status
        sys_info = detector.get_system_info()
        console.print(f"[dim]SYSTEM: {sys_info['distro']} | SHELL: {sys_info['shell']} | ROOT: {sys_info['root']}[/dim]")
        print_divider()
        
        # Menu Options
        print_menu_option("1", "AI OPERATIONS", "Execute security queries & generate scripts")
        print_menu_option("2", "WALLET & CREDITS", f"Balance: {sub_manager.credits} credits")
        print_menu_option("3", "UPGRADE PLAN", "Unlock Operational Mode")
        print_menu_option("4", "BUY CREDITS", "Top up your balance")
        print_menu_option("5", "PROFILE", "User details & History")
        print_menu_option("6", "SETTINGS", "Configuration")
        print_menu_option("7", "MANUAL", "Help & Documentation")
        print_menu_option("0", "EXIT", "Terminate session")
        
        print_divider()

    def _ai_interface(self, sub_manager, ai_handler) -> None:
        """Professional AI Interface."""
        clear_and_show_banner()
        mode = ai_handler.get_mode().value.upper()
        
        print_header(f"AI CONSOLE [{mode}]")
        
        if not sub_manager.is_premium:
            print_info("Running in CONSULTATION MODE (Free).")
            console.print("[dim]Limited to explanations. Upgrade for script generation.[/dim]\n")
        else:
            print_success("OPERATIONAL MODE ACTIVE. Full capability unlocked.")
        
        console.print("[dim]Type 'exit' to return to dashboard.[/dim]\n")
        
        while True:
            query = get_input("CMD/QUERY")
            
            if query.lower() in ['exit', 'quit', 'back']:
                break
            
            if not query:
                continue
            
            with show_loading("Analyzing request & Generating response..."):
                response = ai_handler.get_response(query)
            
            print_ai_response(response, mode)
            
            # Refresh credits
            sub_manager.refresh()
            if not sub_manager.is_premium:
                console.print(f"[dim]Remaining Credits: {sub_manager.credits}[/dim]\n")

    def _show_balance(self, sub_manager) -> None:
        """Show balance."""
        clear_and_show_banner()
        print_header("WALLET STATUS")
        
        details = sub_manager.get_subscription_details()
        
        table = Table(box=box.SIMPLE)
        table.add_column("Resource", style="rgb(0,100,255)")
        table.add_column("Value", style="white bold")
        
        table.add_row("Credits", str(details["credits"]))
        table.add_row("Plan", "PREMIUM" if details["is_premium"] else "FREE")
        
        if details["is_premium"]:
            table.add_row("Expires In", f"{details['days_left']} days")
        
        console.print(table)
        get_input("Press Enter...")

    def _subscription_menu(self, sub_manager) -> None:
        """Subscription Upgrade."""
        from ..subscription import get_plan_comparison
        
        clear_and_show_banner()
        print_header("UPGRADE TO OPERATIONAL")
        
        if sub_manager.is_premium:
            print_success("You are already on the PREMIUM Plan.")
            return
        
        console.print(get_plan_comparison())
        
        if confirm("Initialize Upgrade Sequence ($10/mo)?"):
            sub_manager.start_subscription_flow()
            get_input("Press Enter after payment...")

    def _credits_menu(self, sub_manager) -> None:
        """Buy Credits."""
        from ..subscription import get_credits_packages_display
        from ..config import CREDIT_PACKAGES
        
        clear_and_show_banner()
        print_header("PURCHASE CREDITS")
        console.print(get_credits_packages_display())
        
        choice = get_input("Select Package # (0 to cancel)")
        if choice == "0": return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(CREDIT_PACKAGES):
                sub_manager.start_credits_flow(idx)
                get_input("Press Enter after payment...")
            else:
                print_error("Invalid package")
        except ValueError:
            print_error("Invalid input")

    def _show_profile(self) -> None:
        """Show Profile."""
        from ..database_manager import get_user_profile
        
        clear_and_show_banner()
        print_header("USER PROFILE")
        profile = get_user_profile(self.user_id)
        
        if profile:
            console.print(Panel(
                f"""
[bold]Username:[/bold] {profile['username']}
[bold]ID:[/bold] {profile['id']}
[bold]Created:[/bold] {profile['created_at']}
                """,
                title="Account Details",
                border_style="rgb(0,255,255)"
            ))
        get_input("Press Enter...")

    def _settings_menu(self) -> None:
        """Settings."""
        from ..auth import auth_manager
        from ..distro_detector import detector
        
        clear_and_show_banner()
        print_header("SYSTEM SETTINGS")
        
        # System Info Panel
        sys_info = detector.get_system_info()
        console.print(Panel(
            f"""
[bold]Distro:[/bold] {sys_info['distro']}
[bold]Pkg Manager:[/bold] {sys_info['pkg_manager']}
[bold]Data Dir:[/bold] {detector.get_data_dir()}
            """,
            title="Environment",
            border_style="rgb(0,255,255)"
        ))
        
        if confirm("Logout from this device?"):
            auth_manager.logout()
            self._running = False
            print_success("Logged out.")

    def _show_help(self) -> None:
        """Help."""
        clear_and_show_banner()
        print_header("OPERATIONAL MANUAL")
        console.print("""
[bold rgb(0,100,255)]1. Consultation Mode (Free)[/bold rgb(0,100,255)]
- Theory, basic debugging, learning.
- Rate limited.

[bold rgb(0,255,255)]2. Operational Mode (Premium)[/bold rgb(0,255,255)]
- Script generation, full payload analysis.
- Automation workflow.
- Priority processing.

[bold rgb(0,150,255)]Safety Guidelines[/bold rgb(0,150,255)]
- All actions are logged locally.
- Do not use for illegal activities.
- Ethics filters are active.
        """)
        get_input("Press Enter...")

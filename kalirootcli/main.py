"""
Main entry point for KaliRoot CLI
Uses API backend for all operations.
"""

import sys
import logging
from getpass import getpass

from .api_client import api_client
from .distro_detector import detector
from .ui.display import (
    console, 
    print_banner, 
    print_error, 
    print_success,
    print_info,
    show_loading,
    print_header,
    print_menu_option,
    print_divider,
    print_ai_response,
    get_input,
    confirm
)

# Configure logging
logging.basicConfig(level=logging.WARNING)


def authenticate() -> bool:
    """Handle authentication flow."""
    if api_client.is_logged_in():
        # Verify session is still valid
        with show_loading("Verifying session..."):
            result = api_client.get_status()
        
        if result["success"]:
            print_success(f"Welcome back, {api_client.username}!")
            return True
        else:
            print_info("Session expired. Please login again.")
    
    # Show auth menu
    while True:
        console.print("\n[bold cyan]═══ AUTHENTICATION ═══[/bold cyan]\n")
        print_menu_option("1", "Login")
        print_menu_option("2", "Register")
        print_menu_option("0", "Exit")
        
        choice = get_input("Option")
        
        if choice == "1":
            username = get_input("Username").lower().strip()
            password = getpass("Password: ")
            
            with show_loading("Logging in..."):
                result = api_client.login(username, password)
            
            if result["success"]:
                print_success(f"Welcome, {username}!")
                return True
            else:
                print_error(result["error"])
                
        elif choice == "2":
            username = get_input("Username").lower().strip()
            if len(username) < 3:
                print_error("Username must be at least 3 characters")
                continue
                
            password = getpass("Password: ")
            if len(password) < 6:
                print_error("Password must be at least 6 characters")
                continue
                
            password2 = getpass("Confirm password: ")
            if password != password2:
                print_error("Passwords don't match")
                continue
            
            with show_loading("Creating account..."):
                result = api_client.register(username, password)
            
            if result["success"]:
                print_success(f"Account created! Welcome, {username}!")
                return True
            else:
                print_error(result["error"])
                
        elif choice == "0":
            return False


def main_menu():
    """Main application menu."""
    running = True
    
    while running:
        # Get fresh status
        with show_loading("Loading..."):
            status_result = api_client.get_status()
        
        if not status_result["success"]:
            print_error("Session error. Please restart.")
            break
        
        status = status_result["data"]
        sys_info = detector.get_system_info()
        
        # Render dashboard
        console.clear()
        
        mode = "OPERATIONAL" if status["is_premium"] else "CONSULTATION"
        color = "green" if status["is_premium"] else "yellow"
        
        console.print(f"\n[bold cyan]═══ KALIROOT CLI ═══[/bold cyan]")
        console.print(f"[dim]{sys_info['distro']} | {sys_info['shell']} | {sys_info['root']}[/dim]")
        console.print(f"\n[bold]User:[/bold] {status['username']}")
        console.print(f"[bold]Mode:[/bold] [{color}]{mode}[/{color}]")
        console.print(f"[bold]Credits:[/bold] {status['credits']}")
        
        if status["is_premium"]:
            console.print(f"[bold]Premium:[/bold] [green]{status['days_left']} days left[/green]")
        
        print_divider()
        
        print_menu_option("1", "AI CONSOLE", "Security queries & scripts")
        print_menu_option("2", "UPGRADE", "Get Premium for full access")
        print_menu_option("3", "SETTINGS", "Account & logout")
        print_menu_option("0", "EXIT")
        
        print_divider()
        
        choice = get_input("Select")
        
        if choice == "1":
            ai_console(status)
        elif choice == "2":
            upgrade_menu()
        elif choice == "3":
            if settings_menu():
                running = False
        elif choice == "0":
            if confirm("Exit KaliRoot CLI?"):
                running = False
                console.print("\n[bold cyan]👋 Goodbye![/bold cyan]\n")


def ai_console(status):
    """AI interaction interface."""
    mode = "OPERATIONAL" if status["is_premium"] else "CONSULTATION"
    sys_info = detector.get_system_info()
    
    print_header(f"AI CONSOLE [{mode}]")
    
    if not status["is_premium"]:
        console.print(f"[yellow]Credits: {status['credits']}[/yellow]")
        console.print("[dim]Upgrade to Premium for unlimited queries.[/dim]\n")
    else:
        console.print("[green]Premium Mode - Unlimited queries[/green]\n")
    
    console.print("[dim]Type 'exit' to return to menu.[/dim]\n")
    
    environment = {
        "distro": sys_info.get("distro", "linux"),
        "shell": sys_info.get("shell", "bash"),
        "root": sys_info.get("root", "No"),
        "pkg_manager": sys_info.get("pkg_manager", "apt")
    }
    
    while True:
        query = get_input("Query")
        
        if query.lower() in ['exit', 'quit', 'back']:
            break
        
        if not query:
            continue
        
        with show_loading("Processing..."):
            result = api_client.ai_query(query, environment)
        
        if result["success"]:
            data = result["data"]
            print_ai_response(data["response"], data["mode"])
            
            if data.get("credits_remaining") is not None:
                console.print(f"[dim]Credits remaining: {data['credits_remaining']}[/dim]\n")
        else:
            print_error(result["error"])
            if "credits" in result["error"].lower():
                break


def upgrade_menu():
    """Handle premium upgrade."""
    print_header("UPGRADE TO PREMIUM")
    
    console.print("""
[bold green]PREMIUM BENEFITS:[/bold green]
• Unlimited AI queries
• Full script generation
• Vulnerability analysis
• +250 bonus credits/month
• Priority support

[bold]Price: $10/month (USDT)[/bold]
""")
    
    if confirm("Create payment invoice?"):
        with show_loading("Generating invoice..."):
            result = api_client.create_subscription_invoice()
        
        if result["success"]:
            url = result["data"]["invoice_url"]
            print_success("Invoice created!")
            console.print(f"\n[bold]Payment URL:[/bold]\n{url}\n")
            
            if detector.open_url(url):
                print_info("Browser opened.")
            else:
                print_info("Please copy and open the URL above.")
                
            console.print("[dim]After payment, your account will be upgraded automatically.[/dim]")
        else:
            print_error(result["error"])
    
    get_input("Press Enter to continue...")


def settings_menu() -> bool:
    """Settings menu. Returns True if should exit app."""
    print_header("SETTINGS")
    
    sys_info = detector.get_system_info()
    console.print(f"[bold]System:[/bold] {sys_info['distro']}")
    console.print(f"[bold]User:[/bold] {api_client.username}")
    
    print_divider()
    print_menu_option("1", "Logout")
    print_menu_option("0", "Back")
    
    choice = get_input("Select")
    
    if choice == "1":
        if confirm("Logout?"):
            api_client.logout()
            print_success("Logged out.")
            return True
    
    return False


def main():
    """Application entry point."""
    try:
        console.clear()
        print_banner()
        
        # Detect environment
        sys_info = detector.get_system_info()
        print_info(f"System: {sys_info['distro']} | {sys_info['shell']}")
        
        # Authenticate
        if not authenticate():
            console.print("\n[cyan]Goodbye![/cyan]\n")
            sys.exit(0)
        
        # Main menu
        main_menu()
        
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Interrupted.[/bold cyan]\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {e}")
        logging.exception("Main crash")
        sys.exit(1)


if __name__ == "__main__":
    main()

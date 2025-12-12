#!/usr/bin/env python3
"""
KaliRoot CLI - Main Entry Point
Terminal-based cybersecurity assistant for Termux and Kali Linux.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for KaliRoot CLI."""
    
    # Import after logging setup to capture any import errors
    try:
        from .ui.display import (
            console, 
            print_banner, 
            print_error, 
            print_success,
            print_info,
            print_warning,
            clear_screen,
            get_input
        )
        from .distro_detector import detector
        from .config import validate_config, get_config_status
        from .auth import auth_manager
        from .ui.menus import MainMenu
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    
    # Clear screen and show banner
    clear_screen()
    print_banner()
    
    # Show detected environment
    console.print(f"\n{detector.get_distro_emoji()} [bold]Entorno detectado:[/bold] [cyan]{detector.get_distro_name()}[/cyan]")
    
    # Validate configuration
    missing = validate_config(require_all=False)
    
    if missing:
        print_error("Faltan variables de entorno críticas:")
        for var in missing:
            console.print(f"  [red]• {var}[/red]")
        console.print("\n[yellow]Copia .env.template a .env y configura tus API keys.[/yellow]")
        console.print("[dim]cp .env.template .env && nano .env[/dim]\n")
        sys.exit(1)
    
    # Show config status
    config_status = get_config_status()
    console.print("\n[dim]Servicios:[/dim]")
    console.print(f"  [dim]• Supabase: {'✅' if config_status['supabase'] else '❌'}[/dim]")
    console.print(f"  [dim]• Groq AI: {'✅' if config_status['groq'] else '❌'}[/dim]")
    console.print(f"  [dim]• Pagos: {'✅' if config_status['payments'] else '❌'}[/dim]")
    
    # Test database connection
    console.print("\n[dim]Verificando conexión a base de datos...[/dim]")
    
    try:
        from .database_manager import test_connection
        if not test_connection():
            print_warning("No se pudo conectar a la base de datos.")
            console.print("[yellow]Verifica tus credenciales de Supabase y que las tablas estén creadas.[/yellow]")
            console.print("[dim]Ejecuta supabase_migrations.sql en tu proyecto Supabase.[/dim]\n")
            
            if not get_input("¿Continuar de todos modos? (s/n): ").lower().startswith('s'):
                sys.exit(1)
        else:
            print_success("Conexión a base de datos OK")
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        if not get_input("¿Continuar de todos modos? (s/n): ").lower().startswith('s'):
            sys.exit(1)
    
    # Check for existing session
    session = auth_manager.load_session()
    
    if session:
        console.print(f"\n[green]👋 ¡Bienvenido de vuelta, {session.get('username', 'usuario')}![/green]")
        user_data = session
    else:
        # Need to authenticate
        console.print("\n[dim]No hay sesión activa. Por favor inicia sesión o regístrate.[/dim]")
        user_data = auth_manager.interactive_auth()
        
        if not user_data:
            console.print("\n[cyan]👋 ¡Hasta pronto![/cyan]\n")
            sys.exit(0)
    
    # Start main menu
    try:
        menu = MainMenu(
            user_id=user_data["id"],
            username=user_data.get("username", "user")
        )
        menu.show()
    except KeyboardInterrupt:
        console.print("\n\n[cyan]👋 ¡Hasta pronto, hacker![/cyan]\n")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unexpected error")
        print_error(f"Error inesperado: {e}")
        sys.exit(1)


def cli():
    """CLI entry point for setuptools."""
    main()


if __name__ == "__main__":
    main()

"""
Authentication module for KR-CLI v2.0
Handles user registration with email verification, login, and session management.
Uses Supabase Auth via API backend.
"""

import os
import re
import logging
from typing import Optional
from getpass import getpass

from .api_client import api_client
from .distro_detector import detector

logger = logging.getLogger(__name__)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


class AuthManager:
    """Manages user authentication and sessions via API."""
    
    def __init__(self):
        pass  # Session managed by api_client
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return api_client.is_logged_in()
    
    @property
    def current_user(self) -> Optional[dict]:
        """Get current logged-in user info."""
        if not api_client.is_logged_in():
            return None
        return {
            "id": api_client.user_id,
            "email": api_client.email
        }
    
    def logout(self) -> bool:
        """Log out current user."""
        api_client.logout()
        return True
    
    def interactive_register(self) -> Optional[dict]:
        """
        Interactive registration flow with email verification.
        
        Returns:
            dict with user data if successful, None if failed
        """
        from .ui.display import console, print_error, print_success, print_info, print_warning
        
        console.print("\n[bold cyan]📝 REGISTRO DE USUARIO[/bold cyan]")
        console.print("[dim]Se requiere verificación por correo electrónico[/dim]\n")
        
        # Get email
        while True:
            email = console.input("[cyan]📧 Email: [/cyan]").strip().lower()
            
            if not email:
                print_error("El email no puede estar vacío")
                continue
            
            if not is_valid_email(email):
                print_error("Formato de email inválido")
                continue
            
            break
        
        # Get username (optional)
        username = console.input("[cyan]👤 Username (opcional, Enter para usar email): [/cyan]").strip()
        if not username:
            username = email.split("@")[0]
        
        # Get password
        while True:
            password = getpass("🔐 Password: ")
            
            if len(password) < 6:
                print_error("La contraseña debe tener al menos 6 caracteres")
                continue
            
            password_confirm = getpass("🔐 Confirmar password: ")
            
            if password != password_confirm:
                print_error("Las contraseñas no coinciden")
                continue
            
            break
        
        # Register user via API
        print_info("Registrando usuario...")
        
        result = api_client.register(email, password, username)
        
        if result.get("success"):
            console.print("\n[bold green]✅ ¡REGISTRO EXITOSO![/bold green]\n")
            console.print(f"📧 Enviamos un correo de verificación a: [cyan]{email}[/cyan]")
            console.print("\n[yellow]⚠️  IMPORTANTE:[/yellow]")
            console.print("1. Revisa tu bandeja de entrada (y spam)")
            console.print("2. Haz clic en el enlace de verificación")
            console.print("3. Regresa aquí para iniciar sesión\n")
            
            return {"email": email, "needs_verification": True}
        else:
            print_error(result.get("error", "Error en el registro"))
            return None
    
    def interactive_login(self) -> Optional[dict]:
        """
        Interactive login flow.
        
        Returns:
            dict with user data if successful, None if failed
        """
        from .ui.display import console, print_error, print_success, print_warning, print_info
        
        console.print("\n[bold cyan]🔐 INICIAR SESIÓN[/bold cyan]\n")
        
        # Get email
        email = console.input("[cyan]📧 Email: [/cyan]").strip().lower()
        
        if not email:
            print_error("Email es requerido")
            return None
        
        # Get password
        password = getpass("🔐 Password: ")
        
        # Login via API
        print_info("Conectando...")
        result = api_client.login(email, password)
        
        if result.get("success"):
            print_success(f"¡Bienvenido de vuelta!")
            return result.get("data")
        else:
            error = result.get("error", "")
            print_error(error)
            
            # Offer to resend verification if that's the issue
            if "verifi" in error.lower():
                resend = console.input("\n¿Reenviar correo de verificación? [s/N]: ").strip().lower()
                if resend == "s":
                    res = api_client.resend_verification(email)
                    if res.get("success"):
                        print_info("Correo de verificación reenviado. Revisa tu bandeja.")
                    else:
                        print_error("No se pudo reenviar el correo")
            
            return None
    
    def interactive_auth(self) -> Optional[dict]:
        """
        Combined auth flow - shows menu to login or register.
        
        Returns:
            dict with user data if successful, None if user exits
        """
        from .ui.display import console, print_error
        
        while True:
            console.print("\n[bold yellow]═══════════════════════════════════════[/bold yellow]")
            console.print("[bold yellow]         AUTENTICACIÓN KR-CLI          [/bold yellow]")
            console.print("[bold yellow]═══════════════════════════════════════[/bold yellow]\n")
            
            console.print("  [cyan]1.[/cyan] 🔐 Iniciar sesión")
            console.print("  [cyan]2.[/cyan] 📝 Registrarse (email verificado)")
            console.print("  [cyan]0.[/cyan] ❌ Salir\n")
            
            choice = console.input("[bold]Opción: [/bold]").strip()
            
            if choice == "1":
                result = self.interactive_login()
                if result:
                    return result
            elif choice == "2":
                result = self.interactive_register()
                if result and not result.get("needs_verification"):
                    return result
                # If needs verification, loop back to login
            elif choice == "0":
                return None
            else:
                print_error("Opción no válida")


# Global instance
auth_manager = AuthManager()

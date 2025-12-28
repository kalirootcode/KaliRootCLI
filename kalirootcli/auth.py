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
        from .ui.display import console, print_error, print_success, print_info, print_warning, clear_screen
        
        console.print("\n[bold rgb(0,255,255)]📝 REGISTRO DE USUARIO[/bold rgb(0,255,255)]")
        console.print("[dim]Se requiere verificación por correo electrónico[/dim]\n")
        
        # Get email
        while True:
            email = console.input("[rgb(0,100,255)]📧 Email: [/rgb(0,100,255)]").strip().lower()
            
            if not email:
                print_error("El email no puede estar vacío")
                continue
            
            if not is_valid_email(email):
                print_error("Formato de email inválido")
                continue
            
            break
        
        # Get username (optional)
        username = console.input("[rgb(0,100,255)]👤 Username (opcional, Enter para usar email): [/rgb(0,100,255)]").strip()
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

        
        # ════════════════════════════════════════════════════════════════════
        # TÉRMINOS Y CONDICIONES
        # ════════════════════════════════════════════════════════════════════
        
        terms_text = """
KR-CLI - TÉRMINOS DE USO Y RESPONSABILIDAD
════════════════════════════════════════

1. NATURALEZA DE LA HERRAMIENTA
   KR-CLI (KaliRoot CLI) es una herramienta profesional avanzada diseñada para operaciones
   de ciberseguridad ofensiva y defensiva, análisis forense y pruebas de penetración.

2. RESPONSABILIDAD DEL USUARIO
   • El uso de esta herramienta es responsabilidad EXCLUSIVA del usuario.
   • Te comprometes a utilizar KR-CLI únicamente en:
     - Entornos controlados de laboratorio.
     - Sistemas propios.
     - Infraestructuras donde cuentes con autorización explícita y por escrito.

3. EXENCIÓN DE RESPONSABILIDAD
   • Los creadores, desarrolladores y colaboradores de KR-CLI NO se hacen responsables
     por daños, pérdida de datos, intrusiones no autorizadas o consecuencias legales
     derivadas del mal uso de este software.

4. CUMPLIMIENTO LEGAL
   • Es tu obligación conocer y respetar las leyes locales e internacionales vigentes
     sobre delitos informáticos y ciberseguridad.

AL ACEPTAR, CONFIRMAS QUE:
   ✅ Tienes los conocimientos técnicos necesarios.
   ✅ Entiendes los riesgos asociados.
   ✅ Eximes de toda responsabilidad al equipo de KR-CLI.
"""
        
        clear_screen()
        console.print("[bold red]⚠️  IMPORTANTE: TÉRMINOS Y CONDICIONES DE USO[/bold red]")
        console.print(terms_text)
        console.print("────────────────────────────────────────────────────────────────")
        
        console.print("\n[bold]¿Aceptas estos términos y condiciones?[/bold]\n")
        console.print("  [bold green]1 › ✅ ACEPTAR Y CONTINUAR[/bold green]")
        console.print("  [bold red]2 › ❌ RECHAZAR Y SALIR[/bold red]")
        
        while True:
            choice = console.input("\n[bold cyan]Opción › [/bold cyan]").strip()
            
            if choice == "1":
                break
            elif choice == "2":
                print_warning("Has rechazado los términos. El registro ha sido cancelado.")
                return None
            else:
                console.print("[red]Opción inválida. Selecciona 1 o 2.[/red]")
        
        # Register user via API
        print_info("Registrando usuario y guardando aceptación de términos...")
        
        # Pass terms_accepted=True and the text for logging
        result = api_client.register(email, password, username, terms_accepted=True, terms_text=terms_text)
        
        if result.get("success"):
            console.print("\n[bold green]✅ ¡REGISTRO EXITOSO![/bold green]\n")
            console.print(f"📧 Enviamos un correo de verificación a: [rgb(0,100,255)]{email}[/rgb(0,100,255)]")
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
        
        console.print("\n[bold rgb(0,255,255)]🔐 INICIAR SESIÓN[/bold rgb(0,255,255)]\n")
        
        # Get email
        email = console.input("[rgb(0,100,255)]📧 Email: [/rgb(0,100,255)]").strip().lower()
        
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
        from .ui.display import console, print_error, print_banner, clear_screen, get_input
        
        while True:
            # Clear screen and show banner per user request
            clear_screen()
            print_banner(show_skull=False)
            
            console.print("  [bold rgb(0,100,255)]1.[/bold rgb(0,100,255)] 🔐 Iniciar sesión")
            console.print("  [bold rgb(0,100,255)]2.[/bold rgb(0,100,255)] 📝 Registrarse (email verificado)")
            console.print("  [bold rgb(0,100,255)]0.[/bold rgb(0,100,255)] ❌ Salir\n")
            
            choice = get_input("Opción")
            
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

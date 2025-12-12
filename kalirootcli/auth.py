"""
Authentication module for KaliRoot CLI
Handles user registration, login, and session management.
"""

import os
import json
import logging
import bcrypt
from typing import Optional
from getpass import getpass

from .distro_detector import detector
from .database_manager import register_user, get_user_by_username

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication and sessions."""
    
    def __init__(self):
        self.session_file = detector.get_session_file()
        self._current_user: Optional[dict] = None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def save_session(self, user_data: dict) -> bool:
        """Save user session to local file."""
        try:
            session_data = {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "logged_in": True
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            self._current_user = session_data
            logger.info(f"Session saved for user: {session_data.get('username')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def load_session(self) -> Optional[dict]:
        """Load user session from local file."""
        try:
            if not os.path.exists(self.session_file):
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            if session_data.get("logged_in"):
                self._current_user = session_data
                return session_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return None
    
    def logout(self) -> bool:
        """Remove session and log out."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            
            self._current_user = None
            logger.info("User logged out")
            return True
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False
    
    @property
    def current_user(self) -> Optional[dict]:
        """Get current logged-in user."""
        if self._current_user is None:
            self._current_user = self.load_session()
        return self._current_user
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self.current_user is not None
    
    def interactive_register(self) -> Optional[dict]:
        """
        Interactive registration flow.
        
        Returns:
            dict with user data if successful, None if failed
        """
        from .ui.display import console, print_error, print_success, print_info
        
        console.print("\n[bold cyan]📝 REGISTRO DE USUARIO[/bold cyan]\n")
        
        # Get username
        while True:
            username = console.input("[cyan]Username: [/cyan]").strip().lower()
            
            if not username:
                print_error("El username no puede estar vacío")
                continue
            
            if len(username) < 3:
                print_error("El username debe tener al menos 3 caracteres")
                continue
            
            if not username.isalnum():
                print_error("El username solo puede contener letras y números")
                continue
            
            # Check if username exists
            existing = get_user_by_username(username)
            if existing:
                print_error("Este username ya está registrado")
                continue
            
            break
        
        # Get password
        while True:
            password = getpass("Password: ")
            
            if len(password) < 6:
                print_error("La contraseña debe tener al menos 6 caracteres")
                continue
            
            password_confirm = getpass("Confirmar password: ")
            
            if password != password_confirm:
                print_error("Las contraseñas no coinciden")
                continue
            
            break
        
        # Register user
        print_info("Registrando usuario...")
        
        password_hash = self.hash_password(password)
        result = register_user(username, password_hash)
        
        if result:
            print_success(f"¡Usuario '{username}' registrado exitosamente!")
            self.save_session(result)
            return result
        else:
            print_error("Error al registrar usuario. Intenta con otro username.")
            return None
    
    def interactive_login(self) -> Optional[dict]:
        """
        Interactive login flow.
        
        Returns:
            dict with user data if successful, None if failed
        """
        from .ui.display import console, print_error, print_success, print_warning
        
        console.print("\n[bold cyan]🔐 INICIAR SESIÓN[/bold cyan]\n")
        
        # Get username
        username = console.input("[cyan]Username: [/cyan]").strip().lower()
        
        if not username:
            print_error("Username es requerido")
            return None
        
        # Get password
        password = getpass("Password: ")
        
        # Get user from database
        user = get_user_by_username(username)
        
        if not user:
            print_error("Usuario no encontrado")
            return None
        
        # Verify password
        if not self.verify_password(password, user.get("password_hash", "")):
            print_error("Contraseña incorrecta")
            return None
        
        # Save session
        session_data = {
            "id": user["id"],
            "username": user["username"],
            "credit_balance": user.get("credit_balance", 0),
            "subscription_status": user.get("subscription_status", "free")
        }
        
        self.save_session(session_data)
        print_success(f"¡Bienvenido de vuelta, {username}!")
        
        return session_data
    
    def interactive_auth(self) -> Optional[dict]:
        """
        Combined auth flow - shows menu to login or register.
        
        Returns:
            dict with user data if successful, None if user exits
        """
        from .ui.display import console, print_error
        
        while True:
            console.print("\n[bold yellow]¿Ya tienes cuenta?[/bold yellow]\n")
            console.print("  [cyan]1.[/cyan] Iniciar sesión")
            console.print("  [cyan]2.[/cyan] Registrarse")
            console.print("  [cyan]0.[/cyan] Salir\n")
            
            choice = console.input("[bold]Opción: [/bold]").strip()
            
            if choice == "1":
                result = self.interactive_login()
                if result:
                    return result
            elif choice == "2":
                result = self.interactive_register()
                if result:
                    return result
            elif choice == "0":
                return None
            else:
                print_error("Opción no válida")


# Global instance
auth_manager = AuthManager()

"""
API Client for KR-CLI v2.0
Handles all communication with the backend server.
Now uses email-based authentication with Supabase Auth.
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# API Server URL - Change this to your Render URL
API_BASE_URL = os.getenv("KRCLI_API_URL", "https://kalirootcli.onrender.com")
# API_BASE_URL = os.getenv("KRCLI_API_URL", "http://localhost:8000")


class APIClient:
    """Client for KR-CLI API Backend."""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.email: Optional[str] = None
        self._load_session()
    
    def _get_session_file(self) -> str:
        """Get session file path."""
        if os.path.exists("/data/data/com.termux"):
            base = os.path.expanduser("~/.krcli")
        else:
            base = os.path.expanduser("~/.config/krcli")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "session.json")
    
    def _load_session(self) -> None:
        """Load saved session."""
        try:
            path = self._get_session_file()
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.user_id = data.get("user_id")
                    self.email = data.get("email")
        except Exception as e:
            logger.error(f"Error loading session: {e}")
    
    def _save_session(self) -> None:
        """Save session to file."""
        try:
            path = self._get_session_file()
            with open(path, "w") as f:
                json.dump({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "user_id": self.user_id,
                    "email": self.email
                }, f)
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def is_logged_in(self) -> bool:
        """Check if user has valid session."""
        return self.access_token is not None
    
    def register(self, email: str, password: str, username: str = None, terms_accepted: bool = False, terms_text: str = None) -> Dict[str, Any]:
        """
        Register new user with email.
        Email verification is required before login.
        """
        try:
            payload = {
                "email": email, 
                "password": password,
                "terms_accepted": terms_accepted,
                "terms_text": terms_text
            }
            if username:
                payload["username"] = username
            
            resp = requests.post(
                f"{self.base_url}/api/auth/register",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            data = resp.json()
            
            if resp.status_code == 200 and data.get("success"):
                return {
                    "success": True, 
                    "message": data.get("message", "Registro exitoso. Verifica tu correo."),
                    "user_id": data.get("user_id"),
                    "email": data.get("email"),
                    "needs_verification": True
                }
            else:
                return {
                    "success": False, 
                    "error": data.get("message") or data.get("detail", "Error en registro")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user with email.
        Email must be verified first.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json={"email": email, "password": password},
                timeout=30
            )
            
            data = resp.json()
            
            if resp.status_code == 200 and data.get("success"):
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.user_id = data.get("user_id")
                self.email = data.get("email")
                self._save_session()
                return {"success": True, "data": data}
            else:
                return {
                    "success": False, 
                    "error": data.get("message") or data.get("detail", "Login failed")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def resend_verification(self, email: str) -> Dict[str, Any]:
        """Resend email verification."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/resend-verification",
                params={"email": email},
                timeout=30
            )
            data = resp.json()
            return {"success": data.get("success", False), "message": data.get("message", "")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            return False
        
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/refresh",
                params={"refresh_token": self.refresh_token},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self._save_session()
                return True
            return False
        except:
            return False
    
    def logout(self) -> None:
        """Clear session."""
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.email = None
        try:
            os.remove(self._get_session_file())
        except:
            pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get user status including credits and subscription."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/user/status",
                headers=self._headers(),
                timeout=30
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            elif resp.status_code == 401:
                # Try to refresh token
                if self.refresh_access_token():
                    return self.get_status()
                self.logout()
                return {"success": False, "error": "Sesión expirada. Por favor inicia sesión de nuevo."}
            else:
                return {"success": False, "error": resp.json().get("detail", "Error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def ai_query(self, query: str, environment: Dict[str, str]) -> Dict[str, Any]:
        """Send AI query."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/ai/query",
                headers=self._headers(),
                json={"query": query, "environment": environment},
                timeout=120
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            elif resp.status_code == 402:
                return {"success": False, "error": "Sin créditos disponibles. Actualiza a Premium."}
            elif resp.status_code == 401:
                if self.refresh_access_token():
                    return self.ai_query(query, environment)
                self.logout()
                return {"success": False, "error": "Sesión expirada"}
            else:
                return {"success": False, "error": resp.json().get("detail", "Error de IA")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_subscription_invoice(self) -> Dict[str, Any]:
        """Create subscription payment invoice (USDT)."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/payments/create-subscription",
                headers=self._headers(),
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True, 
                    "invoice_url": data.get("invoice_url"),
                    "invoice_id": data.get("invoice_id"),
                    "amount": data.get("amount"),
                    "currency": data.get("currency", "USDT")
                }
            elif resp.status_code == 401:
                if self.refresh_access_token():
                    return self.create_subscription_invoice()
                self.logout()
                return {"success": False, "error": "Sesión expirada"}
            else:
                return {"success": False, "error": resp.json().get("detail", "Error de pago")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_credits_invoice(self, amount: float, credits: int) -> Dict[str, Any]:
        """Create credit pack payment invoice (USDT)."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/payments/create-credits",
                headers=self._headers(),
                json={"amount": float(amount), "credits": int(credits)},
                timeout=30
            )
            
            try:
                data = resp.json()
            except ValueError:
                return {"success": False, "error": f"Invalid API Response: {resp.text[:100]}"}

            if resp.status_code == 200:
                return {
                    "success": True, 
                    "invoice_url": data.get("invoice_url"),
                    "invoice_id": data.get("invoice_id"),
                    "amount": data.get("amount"),
                    "credits": data.get("credits"),
                    "currency": data.get("currency", "USDT")
                }
            elif resp.status_code == 401:
                if self.refresh_access_token():
                    return self.create_credits_invoice(amount, credits)
                self.logout()
                return {"success": False, "error": "Sesión expirada"}
            else:
                return {"success": False, "error": data.get("detail", "Error de pago")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check payment status for an invoice."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/payments/check-status/{invoice_id}",
                headers=self._headers(),
                timeout=30
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            else:
                return {"success": False, "error": resp.json().get("detail", "Error")}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
api_client = APIClient()

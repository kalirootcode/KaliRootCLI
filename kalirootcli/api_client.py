"""
API Client for KaliRoot CLI
Handles all communication with the backend server.
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# API Server URL - Change this to your Render URL
API_BASE_URL = os.getenv("KALIROOTCLI_API_URL", "https://kalirootcli.onrender.com")


class APIClient:
    """Client for KaliRoot API Backend."""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.username: Optional[str] = None
        self._load_session()
    
    def _get_session_file(self) -> str:
        """Get session file path."""
        if os.path.exists("/data/data/com.termux"):
            base = os.path.expanduser("~/.kalirootcli")
        else:
            base = os.path.expanduser("~/.config/kalirootcli")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "session.json")
    
    def _load_session(self) -> None:
        """Load saved session."""
        try:
            path = self._get_session_file()
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    self.user_id = data.get("user_id")
                    self.username = data.get("username")
        except Exception as e:
            logger.error(f"Error loading session: {e}")
    
    def _save_session(self) -> None:
        """Save session to file."""
        try:
            path = self._get_session_file()
            with open(path, "w") as f:
                json.dump({
                    "token": self.token,
                    "user_id": self.user_id,
                    "username": self.username
                }, f)
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def is_logged_in(self) -> bool:
        """Check if user has valid session."""
        return self.token is not None
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """Register new user."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/register",
                headers=self._headers(),
                json={"username": username, "password": password},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.token = data["access_token"]
                self.user_id = data["user_id"]
                self.username = data["username"]
                self._save_session()
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": resp.json().get("detail", "Registration failed")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/auth/login",
                headers=self._headers(),
                json={"username": username, "password": password},
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.token = data["access_token"]
                self.user_id = data["user_id"]
                self.username = data["username"]
                self._save_session()
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": resp.json().get("detail", "Login failed")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout(self) -> None:
        """Clear session."""
        self.token = None
        self.user_id = None
        self.username = None
        try:
            os.remove(self._get_session_file())
        except:
            pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get user status."""
        try:
            resp = requests.get(
                f"{self.base_url}/api/user/status",
                headers=self._headers(),
                timeout=30
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            elif resp.status_code == 401:
                self.logout()
                return {"success": False, "error": "Session expired"}
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
                timeout=60
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            elif resp.status_code == 402:
                return {"success": False, "error": "No credits available. Please upgrade to Premium."}
            elif resp.status_code == 401:
                self.logout()
                return {"success": False, "error": "Session expired"}
            else:
                return {"success": False, "error": resp.json().get("detail", "AI error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_subscription_invoice(self) -> Dict[str, Any]:
        """Create subscription payment invoice."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/payments/create-subscription",
                headers=self._headers(),
                timeout=30
            )
            
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            else:
                return {"success": False, "error": resp.json().get("detail", "Payment error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
api_client = APIClient()

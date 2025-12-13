"""
KaliRoot CLI API Backend
Handles all authentication, AI queries, and payments for the CLI.
Deploy this to Render.
"""

import os
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
import jwt

load_dotenv()

# ===== CONFIG =====
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "kalirootcli-secret-key-change-me")

# ===== INIT =====
app = FastAPI(
    title="KaliRoot CLI API",
    description="Backend API for KaliRoot CLI - Cybersecurity Assistant",
    version="1.0.0"
)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

# ===== MODELS =====
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AIQueryRequest(BaseModel):
    query: str
    environment: dict = {}

class TokenResponse(BaseModel):
    access_token: str
    user_id: str
    username: str
    credits: int
    is_premium: bool

# ===== AUTH HELPERS =====
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===== ENDPOINTS =====

@app.get("/")
async def health():
    return {"status": "ok", "service": "KaliRoot CLI API", "version": "1.0.0"}

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    """Register a new user."""
    # Check if username exists
    existing = supabase.table("cli_users").select("id").eq("username", req.username.lower()).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    password_hash = hash_password(req.password)
    result = supabase.table("cli_users").insert({
        "username": req.username.lower(),
        "password_hash": password_hash,
        "credit_balance": 5,
        "subscription_status": "free"
    }).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Registration failed")
    
    user = result.data[0]
    token = create_token(user["id"], user["username"])
    
    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
        credits=user["credit_balance"],
        is_premium=False
    )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Login and get token."""
    result = supabase.table("cli_users").select("*").eq("username", req.username.lower()).execute()
    
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = result.data[0]
    
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check subscription status
    is_premium = user.get("subscription_status") == "active"
    if user.get("subscription_expires"):
        expires = datetime.fromisoformat(user["subscription_expires"].replace("Z", "+00:00"))
        is_premium = is_premium and expires > datetime.now(expires.tzinfo)
    
    token = create_token(user["id"], user["username"])
    
    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
        credits=user["credit_balance"],
        is_premium=is_premium
    )

@app.get("/api/user/status")
async def get_user_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user status."""
    payload = verify_token(credentials)
    user_id = payload["sub"]
    
    result = supabase.table("cli_users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result.data[0]
    is_premium = user.get("subscription_status") == "active"
    days_left = 0
    
    if user.get("subscription_expires"):
        expires = datetime.fromisoformat(user["subscription_expires"].replace("Z", "+00:00"))
        is_premium = is_premium and expires > datetime.now(expires.tzinfo)
        if is_premium:
            days_left = (expires - datetime.now(expires.tzinfo)).days
    
    return {
        "user_id": user["id"],
        "username": user["username"],
        "credits": user["credit_balance"],
        "is_premium": is_premium,
        "days_left": days_left
    }

@app.post("/api/ai/query")
async def ai_query(req: AIQueryRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Process AI query."""
    payload = verify_token(credentials)
    user_id = payload["sub"]
    
    # Get user
    result = supabase.table("cli_users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result.data[0]
    is_premium = user.get("subscription_status") == "active"
    credits = user.get("credit_balance", 0)
    
    # Check if can query
    if not is_premium and credits <= 0:
        raise HTTPException(status_code=402, detail="No credits available")
    
    # Build system prompt based on environment and mode
    mode = "OPERATIONAL" if is_premium else "CONSULTATION"
    env = req.environment
    
    system_prompt = f"""Eres KaliRoot, un asistente de ciberseguridad experto.

ENTORNO DEL USUARIO:
- Sistema: {env.get('distro', 'Linux')}
- Shell: {env.get('shell', 'bash')}
- Root: {env.get('root', 'No')}
- Gestor de paquetes: {env.get('pkg_manager', 'apt')}

MODO: {mode}
{"Puedes generar scripts completos y comandos operacionales." if is_premium else "Solo proporciona explicaciones teóricas. Para scripts completos, el usuario necesita Premium."}

REGLAS:
1. Responde en español técnico
2. Usa formato Markdown para código
3. Rechaza solicitudes ilegales (malware, DDoS, fraude)
4. Adapta comandos al entorno del usuario
"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.query}
            ],
            max_tokens=2048,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Deduct credit if not premium
        if not is_premium:
            supabase.table("cli_users").update({
                "credit_balance": credits - 1
            }).eq("id", user_id).execute()
        
        return {
            "response": ai_response,
            "mode": mode,
            "credits_remaining": credits - 1 if not is_premium else None
        }
        
    except Exception as e:
        logger.error(f"AI query error: {e}")
        raise HTTPException(status_code=500, detail="AI service error")

@app.post("/api/payments/create-subscription")
async def create_subscription_invoice(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create subscription payment invoice."""
    import requests
    import time
    
    payload = verify_token(credentials)
    user_id = payload["sub"]
    
    nowpayments_key = os.getenv("NOWPAYMENTS_API_KEY")
    if not nowpayments_key:
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    api_url = "https://api.nowpayments.io/v1" if not nowpayments_key.startswith("sandbox") else "https://api-sandbox.nowpayments.io/v1"
    
    invoice_payload = {
        "price_amount": 10.0,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": f"cli_{user_id}_subscription_{int(time.time())}",
        "order_description": "KaliRoot CLI Premium - 30 días"
    }
    
    resp = requests.post(
        f"{api_url}/invoice",
        headers={"x-api-key": nowpayments_key, "Content-Type": "application/json"},
        json=invoice_payload,
        timeout=30
    )
    
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to create invoice")
    
    data = resp.json()
    return {
        "invoice_url": data.get("invoice_url"),
        "invoice_id": data.get("id")
    }

@app.post("/webhook/nowpayments")
async def nowpayments_webhook(request: Request):
    """Handle NowPayments IPN callback."""
    try:
        body = await request.body()
        data = await request.json()
        
        # Verify signature
        signature = request.headers.get("x-nowpayments-sig", "")
        if IPN_SECRET_KEY:
            expected = hmac.new(IPN_SECRET_KEY.encode(), body, hashlib.sha512).hexdigest()
            if signature != expected:
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        status = data.get("payment_status")
        if status not in ["finished", "confirmed"]:
            return {"status": "ignored"}
        
        order_id = data.get("order_id", "")
        parts = order_id.split("_")
        if len(parts) < 3 or parts[0] != "cli":
            return {"status": "ignored"}
        
        user_id = parts[1]
        payment_type = parts[2]
        
        if payment_type == "subscription":
            # Activate subscription
            expires = datetime.utcnow() + timedelta(days=30)
            supabase.table("cli_users").update({
                "subscription_status": "active",
                "subscription_expires": expires.isoformat(),
                "credit_balance": supabase.table("cli_users").select("credit_balance").eq("id", user_id).execute().data[0]["credit_balance"] + 250
            }).eq("id", user_id).execute()
            logger.info(f"Activated subscription for {user_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

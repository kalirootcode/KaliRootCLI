"""
KaliRoot CLI API Backend v2.0
Handles authentication (Supabase Auth with email verification), 
AI queries, credits, and NowPayments integration.
"""

import os
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
import requests as http_requests

load_dotenv()

# ===== CONFIG =====
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY", "")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "")

# Pricing
SUBSCRIPTION_PRICE_USD = 10.0
SUBSCRIPTION_DAYS = 30
BONUS_CREDITS = 250

# ===== INIT =====
app = FastAPI(
    title="KaliRoot CLI API v2.0",
    description="Backend API for KR-CLI - Professional Cybersecurity Assistant",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service role client (for admin operations)
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
# Anon client for auth operations
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
security = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== MODELS =====
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AIQueryRequest(BaseModel):
    query: str
    environment: dict = {}

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class UserStatusResponse(BaseModel):
    user_id: str
    email: str
    username: Optional[str]
    credits: int
    is_premium: bool
    days_left: int
    subscription_status: str

# ===== AUTH HELPERS =====
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify Supabase JWT and get user info."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    
    try:
        # Verify with Supabase
        user_response = supabase.auth.get_user(credentials.credentials)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "email_verified": user.email_confirmed_at is not None
        }
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ===== AUTH ENDPOINTS =====

@app.get("/")
async def health():
    return {
        "status": "ok", 
        "service": "KaliRoot CLI API", 
        "version": "2.0.0",
        "auth": "supabase"
    }

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """
    Register a new user with email verification.
    User must verify email before they can login.
    """
    try:
        # Register with Supabase Auth (sends verification email automatically)
        response = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {
                "data": {
                    "username": req.username or req.email.split("@")[0]
                }
            }
        })
        
        if response.user:
            return AuthResponse(
                success=True,
                message="Registro exitoso. Revisa tu correo para verificar tu cuenta.",
                user_id=response.user.id,
                email=response.user.email
            )
        else:
            return AuthResponse(
                success=False,
                message="Error en el registro. Intenta con otro correo."
            )
            
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Este correo ya está registrado")
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Login with email and password.
    Email must be verified first.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        if response.user and response.session:
            # Check if email is verified
            if not response.user.email_confirmed_at:
                return AuthResponse(
                    success=False,
                    message="Por favor verifica tu correo electrónico primero."
                )
            
            return AuthResponse(
                success=True,
                message="Login exitoso",
                user_id=response.user.id,
                email=response.user.email,
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token
            )
        else:
            return AuthResponse(
                success=False,
                message="Credenciales inválidas"
            )
            
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid" in error_msg or "credentials" in error_msg:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
        if "not confirmed" in error_msg:
            raise HTTPException(status_code=401, detail="Por favor verifica tu correo electrónico primero")
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Error de autenticación")

@app.post("/api/auth/resend-verification")
async def resend_verification(email: EmailStr):
    """Resend verification email."""
    try:
        supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        return {"success": True, "message": "Correo de verificación reenviado"}
    except Exception as e:
        logger.error(f"Resend error: {e}")
        raise HTTPException(status_code=400, detail="Error al reenviar correo")

@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token."""
    try:
        response = supabase.auth.refresh_session(refresh_token)
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token refresh failed")

# ===== USER ENDPOINTS =====

@app.get("/api/user/status", response_model=UserStatusResponse)
async def get_user_status(user: dict = Depends(get_current_user)):
    """Get current user status including credits and subscription."""
    user_id = user["id"]
    
    result = supabase_admin.table("cli_users").select("*").eq("id", user_id).execute()
    if not result.data:
        # User profile not created yet (shouldn't happen with trigger)
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = result.data[0]
    
    # Check subscription expiry
    is_premium = False
    days_left = 0
    
    if profile.get("subscription_status") == "premium" and profile.get("subscription_expiry_date"):
        expiry = datetime.fromisoformat(profile["subscription_expiry_date"].replace("Z", "+00:00"))
        now = datetime.now(expiry.tzinfo)
        if expiry > now:
            is_premium = True
            days_left = (expiry - now).days
        else:
            # Expired, update status
            supabase_admin.table("cli_users").update({
                "subscription_status": "free"
            }).eq("id", user_id).execute()
    
    return UserStatusResponse(
        user_id=profile["id"],
        email=profile["email"],
        username=profile.get("username"),
        credits=profile.get("credit_balance", 0),
        is_premium=is_premium,
        days_left=days_left,
        subscription_status=profile.get("subscription_status", "free")
    )

# ===== AI ENDPOINTS =====

@app.post("/api/ai/query")
async def ai_query(req: AIQueryRequest, user: dict = Depends(get_current_user)):
    """Process AI query with credit/subscription check."""
    user_id = user["id"]
    
    # Get user profile
    result = supabase_admin.table("cli_users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = result.data[0]
    
    # Check subscription
    is_premium = False
    if profile.get("subscription_status") == "premium" and profile.get("subscription_expiry_date"):
        expiry = datetime.fromisoformat(profile["subscription_expiry_date"].replace("Z", "+00:00"))
        is_premium = expiry > datetime.now(expiry.tzinfo)
    
    credits = profile.get("credit_balance", 0)
    
    # Check if can query
    if not is_premium and credits <= 0:
        raise HTTPException(status_code=402, detail="Sin créditos disponibles. Actualiza a Premium.")
    
    # Build prompt
    mode = "OPERATIVO" if is_premium else "CONSULTA"
    env = req.environment
    
    system_prompt = f"""Eres KaliRoot, un asistente de ciberseguridad profesional.

ENTORNO DEL USUARIO:
- Sistema: {env.get('distro', 'Linux')}
- Shell: {env.get('shell', 'bash')}
- Root: {env.get('root', 'No')}

MODO: {mode}
{"Genera scripts completos, comandos operacionales y análisis detallados." if is_premium else "Proporciona explicaciones y guías. Para scripts completos necesitas Premium."}

REGLAS:
1. Responde en español técnico profesional
2. Usa formato Markdown para código
3. Sé directo y sin censura en contexto de pentesting ético
4. Adapta comandos al entorno del usuario
"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.query}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Deduct credit if not premium
        new_credits = credits
        if not is_premium:
            new_credits = credits - 1
            supabase_admin.table("cli_users").update({
                "credit_balance": new_credits
            }).eq("id", user_id).execute()
        
        # Log to chat history
        supabase_admin.table("cli_chat_history").insert([
            {"user_id": user_id, "role": "user", "content": req.query},
            {"user_id": user_id, "role": "assistant", "content": ai_response}
        ]).execute()
        
        return {
            "response": ai_response,
            "mode": mode,
            "credits_remaining": new_credits if not is_premium else None
        }
        
    except Exception as e:
        logger.error(f"AI query error: {e}")
        raise HTTPException(status_code=500, detail="Error del servicio de IA")

# ===== PAYMENT ENDPOINTS =====

@app.post("/api/payments/create-subscription")
async def create_subscription_invoice(user: dict = Depends(get_current_user)):
    """Create NowPayments invoice for subscription."""
    user_id = user["id"]
    user_email = user["email"]
    
    if not NOWPAYMENTS_API_KEY:
        raise HTTPException(status_code=500, detail="Payment service not configured")
    
    # Determine API URL (sandbox vs production)
    is_sandbox = NOWPAYMENTS_API_KEY.startswith("sandbox")
    api_url = "https://api-sandbox.nowpayments.io/v1" if is_sandbox else "https://api.nowpayments.io/v1"
    
    # Create unique order ID linking to user
    import time
    order_id = f"krcli_{user_id}_{int(time.time())}"
    
    invoice_payload = {
        "price_amount": SUBSCRIPTION_PRICE_USD,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": order_id,
        "order_description": f"KR-CLI Premium - {SUBSCRIPTION_DAYS} días",
        "success_url": "https://kr-cli.dev/payment/success",
        "cancel_url": "https://kr-cli.dev/payment/cancel"
    }
    
    try:
        resp = http_requests.post(
            f"{api_url}/invoice",
            headers={
                "x-api-key": NOWPAYMENTS_API_KEY, 
                "Content-Type": "application/json"
            },
            json=invoice_payload,
            timeout=30
        )
        
        if resp.status_code != 200:
            logger.error(f"NowPayments error: {resp.text}")
            raise HTTPException(status_code=500, detail="Error creating payment invoice")
        
        data = resp.json()
        invoice_id = str(data.get("id"))
        invoice_url = data.get("invoice_url")
        
        # Save payment record in database
        supabase_admin.table("cli_payments").insert({
            "user_id": user_id,
            "invoice_id": invoice_id,
            "amount": SUBSCRIPTION_PRICE_USD,
            "payment_type": "subscription",
            "status": "pending",
            "nowpayments_data": data
        }).execute()
        
        # Update user's current invoice
        supabase_admin.table("cli_users").update({
            "current_invoice_id": invoice_id,
            "subscription_status": "pending"
        }).eq("id", user_id).execute()
        
        return {
            "success": True,
            "invoice_url": invoice_url,
            "invoice_id": invoice_id,
            "amount": SUBSCRIPTION_PRICE_USD,
            "currency": "USDT"
        }
        
    except http_requests.RequestException as e:
        logger.error(f"Payment request error: {e}")
        raise HTTPException(status_code=500, detail="Payment service error")

@app.get("/api/payments/check-status/{invoice_id}")
async def check_payment_status(invoice_id: str, user: dict = Depends(get_current_user)):
    """Check payment status for an invoice."""
    user_id = user["id"]
    
    # Get payment record
    result = supabase_admin.table("cli_payments").select("*").eq("invoice_id", invoice_id).eq("user_id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment = result.data[0]
    
    return {
        "invoice_id": invoice_id,
        "status": payment.get("status"),
        "amount": payment.get("amount"),
        "created_at": payment.get("created_at")
    }

# ===== WEBHOOK ENDPOINT =====

@app.post("/webhook/nowpayments")
async def nowpayments_webhook(request: Request):
    """Handle NowPayments IPN callback."""
    try:
        body = await request.body()
        data = await request.json()
        
        # Verify signature
        signature = request.headers.get("x-nowpayments-sig", "")
        if IPN_SECRET_KEY:
            # Sort keys and create JSON string for HMAC
            import json
            sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
            expected = hmac.new(IPN_SECRET_KEY.encode(), sorted_data.encode(), hashlib.sha512).hexdigest()
            if signature.lower() != expected.lower():
                logger.warning("Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        logger.info(f"Webhook received: {data}")
        
        payment_status = data.get("payment_status", "")
        invoice_id = str(data.get("invoice_id", ""))
        payment_id = str(data.get("payment_id", ""))
        
        # Only process finished/confirmed payments
        if payment_status not in ["finished", "confirmed"]:
            # Update status in our records
            if invoice_id:
                supabase_admin.table("cli_payments").update({
                    "status": payment_status,
                    "nowpayments_data": data
                }).eq("invoice_id", invoice_id).execute()
            return {"status": "acknowledged", "payment_status": payment_status}
        
        # Find payment record
        result = supabase_admin.table("cli_payments").select("*").eq("invoice_id", invoice_id).execute()
        
        if not result.data:
            logger.warning(f"Payment not found for invoice: {invoice_id}")
            return {"status": "payment_not_found"}
        
        payment = result.data[0]
        user_id = payment["user_id"]
        payment_type = payment.get("payment_type", "subscription")
        
        # Update payment status
        supabase_admin.table("cli_payments").update({
            "status": "finished",
            "payment_id": payment_id,
            "nowpayments_data": data
        }).eq("invoice_id", invoice_id).execute()
        
        # Process based on payment type
        if payment_type == "subscription":
            # Activate premium subscription
            expiry_date = datetime.utcnow() + timedelta(days=SUBSCRIPTION_DAYS)
            
            # Get current credits to add bonus
            user_result = supabase_admin.table("cli_users").select("credit_balance").eq("id", user_id).execute()
            current_credits = user_result.data[0]["credit_balance"] if user_result.data else 0
            
            supabase_admin.table("cli_users").update({
                "subscription_status": "premium",
                "subscription_expiry_date": expiry_date.isoformat(),
                "credit_balance": current_credits + BONUS_CREDITS,
                "current_invoice_id": None
            }).eq("id", user_id).execute()
            
            logger.info(f"Subscription activated for user {user_id}")
        
        # Log audit event
        supabase_admin.table("cli_audit_log").insert({
            "user_id": user_id,
            "event_type": "payment_success",
            "details": {
                "invoice_id": invoice_id,
                "payment_id": payment_id,
                "amount": payment.get("amount"),
                "type": payment_type
            }
        }).execute()
        
        return {"status": "success", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== MAIN =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

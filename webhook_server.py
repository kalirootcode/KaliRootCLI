"""
Webhook Server for KaliRoot CLI Payments
Handles NowPayments callbacks to activate subscriptions.
"""

import os
import hmac
import hashlib
import logging
from fastapi import FastAPI, Request, HTTPException
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
IPN_SECRET_KEY = os.getenv("IPN_SECRET_KEY", "")

# Initialize
app = FastAPI(title="KaliRoot CLI Webhook")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
logger = logging.getLogger(__name__)

@app.get("/")
async def health():
    return {"status": "ok", "service": "KaliRoot CLI Webhook"}

@app.post("/webhook/nowpayments")
async def nowpayments_webhook(request: Request):
    """Handle NowPayments IPN callback."""
    try:
        body = await request.body()
        data = await request.json()
        
        # Verify signature
        signature = request.headers.get("x-nowpayments-sig", "")
        if IPN_SECRET_KEY:
            expected = hmac.new(
                IPN_SECRET_KEY.encode(),
                body,
                hashlib.sha512
            ).hexdigest()
            if signature != expected:
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Check payment status
        status = data.get("payment_status")
        if status not in ["finished", "confirmed"]:
            return {"status": "ignored", "reason": f"status={status}"}
        
        # Parse order_id: cli_{user_id}_{type}_{timestamp}
        order_id = data.get("order_id", "")
        parts = order_id.split("_")
        if len(parts) < 3 or parts[0] != "cli":
            return {"status": "ignored", "reason": "not cli order"}
        
        user_id = parts[1]
        payment_type = parts[2]
        
        if payment_type == "subscription":
            # Activate subscription
            supabase.rpc("activate_cli_subscription", {
                "p_user_id": user_id,
                "p_invoice_id": str(data.get("payment_id", ""))
            }).execute()
            logger.info(f"Activated subscription for {user_id}")
            
        elif "credits" in payment_type:
            # Add credits
            credits = int(payment_type.replace("credits", ""))
            supabase.rpc("add_cli_credits", {
                "p_user_id": user_id,
                "p_amount": credits
            }).execute()
            logger.info(f"Added {credits} credits to {user_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

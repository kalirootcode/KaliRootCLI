"""
Payment Handler for KaliRoot CLI
Handles NowPayments integration for subscriptions and credit purchases.
"""

import time
import logging
import requests
from typing import Optional

from .config import NOWPAYMENTS_API_KEY, IPN_SECRET_KEY
from .distro_detector import detector

logger = logging.getLogger(__name__)

# Determine API URL based on key type
if NOWPAYMENTS_API_KEY and NOWPAYMENTS_API_KEY.startswith("sandbox"):
    NOWPAYMENTS_API_URL = "https://api-sandbox.nowpayments.io/v1"
else:
    NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"


class PaymentManager:
    """Manages payment operations with NowPayments."""
    
    def __init__(self):
        self.api_key = NOWPAYMENTS_API_KEY
        self.api_url = NOWPAYMENTS_API_URL
    
    def _get_headers(self) -> dict:
        """Get API headers."""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_payment_invoice(
        self, 
        amount_usd: float, 
        user_id: str, 
        description: str = "subscription"
    ) -> Optional[dict]:
        """
        Create a payment invoice on NowPayments.
        
        Args:
            amount_usd: Amount in USD
            user_id: User ID for tracking
            description: Type of purchase (subscription, 400_credits, etc.)
        
        Returns:
            dict with invoice_url, invoice_id, or None on failure
        """
        if not self.api_key:
            logger.error("NOWPAYMENTS_API_KEY is not configured")
            return None
        
        # Build order description
        if description == "subscription":
            order_desc = "Suscripción Premium KaliRoot CLI (30 días + 250 créditos)"
        elif "credits" in description:
            credits_amount = description.split("_")[0]
            order_desc = f"Recarga de {credits_amount} Créditos IA - KaliRoot CLI"
        else:
            order_desc = f"KaliRoot CLI - {description}"
        
        payload = {
            "price_amount": amount_usd,
            "price_currency": "usd",
            "pay_currency": "usdttrc20",  # USDT on TRC-20
            "order_id": f"cli_{user_id}_{description}_{int(time.time())}",
            "order_description": order_desc
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/invoice",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            result = {
                "invoice_url": data.get("invoice_url"),
                "invoice_id": data.get("id"),
                "payment_type": description
            }
            
            logger.info(f"Created invoice {result['invoice_id']} for user {user_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating invoice: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating invoice: {e}")
            return None
    
    def create_subscription_invoice(self, user_id: str) -> Optional[dict]:
        """Create subscription invoice ($10/month)."""
        return self.create_payment_invoice(10.0, user_id, "subscription")
    
    def create_credits_invoice(
        self, 
        user_id: str, 
        credits: int, 
        price: float
    ) -> Optional[dict]:
        """Create credits purchase invoice."""
        return self.create_payment_invoice(price, user_id, f"{credits}_credits")
    
    def open_payment_url(self, url: str) -> bool:
        """
        Open payment URL in browser.
        
        Returns:
            True if opened successfully
        """
        return detector.open_url(url)
    
    def get_payment_status(self, payment_id: str) -> Optional[str]:
        """
        Check payment status.
        
        Returns:
            Status string or None on error
        """
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/payment/{payment_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("payment_status")
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return None
    
    def check_invoice_status(self, invoice_id: str) -> Optional[dict]:
        """
        Check invoice status and payments.
        
        Returns:
            dict with status info or None
        """
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/invoice/{invoice_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Check payments associated with invoice
            payments = data.get("payments", [])
            
            for payment in payments:
                status = payment.get("payment_status")
                if status in ["finished", "confirmed"]:
                    return {
                        "status": "paid",
                        "payment_id": payment.get("payment_id"),
                        "amount": payment.get("actually_paid")
                    }
            
            return {
                "status": "pending",
                "invoice_id": invoice_id
            }
            
        except Exception as e:
            logger.error(f"Error checking invoice status: {e}")
            return None


# Global instance
payment_manager = PaymentManager()


def create_subscription_invoice(user_id: str) -> Optional[dict]:
    """Convenience function to create subscription invoice."""
    return payment_manager.create_subscription_invoice(user_id)


def create_credits_invoice(user_id: str, credits: int, price: float) -> Optional[dict]:
    """Convenience function to create credits invoice."""
    return payment_manager.create_credits_invoice(user_id, credits, price)


def open_payment_url(url: str) -> bool:
    """Convenience function to open payment URL."""
    return payment_manager.open_payment_url(url)

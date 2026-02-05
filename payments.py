import requests
import sqlite3
import logging
from datetime import datetime, timedelta
from config import PAYSTACK_SECRET_KEY, DB_PATH

class PaystackManager:
    BASE_URL = "https://api.paystack.co"
    HEADERS = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    @staticmethod
    def initialize_transaction(email, amount_usd, metadata):
        """Initialize a transaction with Paystack."""
        # Convert USD to cents (Paystack uses the smallest currency unit)
        amount = int(amount_usd * 100)
        
        url = f"{PaystackManager.BASE_URL}/transaction/initialize"
        data = {
            "email": email,
            "amount": amount,
            "currency": "USD",
            "metadata": metadata
        }
        
        logging.info(f"Initializing Paystack transaction for {email} with amount {amount}")
        try:
            response = requests.post(url, headers=PaystackManager.HEADERS, json=data)
            res_json = response.json()
            if not res_json.get('status'):
                logging.error(f"Paystack Error: {res_json.get('message')}")
            return res_json
        except Exception as e:
            logging.error(f"Request Exception: {e}")
            return {"status": False, "message": str(e)}

    @staticmethod
    def verify_transaction(reference):
        """Verify a transaction with Paystack."""
        url = f"{PaystackManager.BASE_URL}/transaction/verify/{reference}"
        response = requests.get(url, headers=PaystackManager.HEADERS)
        return response.json()

    @staticmethod
    def activate_subscription(telegram_id, plan_type):
        """Update user status in database after successful payment."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if plan_type == "trial":
            days = 30
            trial_used = 1
        elif plan_type == "quarterly":
            days = 90
            trial_used = 1
        else:
            days = 30
            trial_used = 0
            
        expiry_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('''
            UPDATE users 
            SET is_subscribed = 1, expiry_date = ?, trial_used = ? 
            WHERE telegram_id = ?
        ''', (expiry_date, trial_used, telegram_id))
        
        conn.commit()
        conn.close()
        return expiry_date

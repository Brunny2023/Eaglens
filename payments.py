import requests
import sqlite3
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
        
        response = requests.post(url, headers=PaystackManager.HEADERS, json=data)
        return response.json()

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

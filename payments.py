import requests
import sqlite3
import logging
import uuid
from datetime import datetime, timedelta
from config import FLW_SECRET_KEY, DB_PATH, CURRENCY

class PaymentManager:
    BASE_URL = "https://api.flutterwave.com/v3"
    HEADERS = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    @staticmethod
    def initialize_transaction(email, amount, metadata):
        """Initialize a transaction with Flutterwave."""
        tx_ref = str(uuid.uuid4())
        url = f"{PaymentManager.BASE_URL}/payments"
        
        data = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": CURRENCY,
            "redirect_url": "https://t.me/EaglensBot", # Redirect back to bot
            "meta": metadata,
            "customer": {
                "email": email,
            },
            "customizations": {
                "title": "Eaglens Subscription",
                "description": f"Payment for {metadata.get('plan', 'subscription')} plan",
                "logo": "https://raw.githubusercontent.com/Brunny2023/Eaglens/main/eaglens_logo.png"
            }
        }
        
        logging.info(f"Initializing Flutterwave transaction for {email} with amount {amount}")
        try:
            response = requests.post(url, headers=PaymentManager.HEADERS, json=data)
            res_json = response.json()
            if res_json.get('status') == 'success':
                # Add tx_ref to response for verification later
                res_json['data']['reference'] = tx_ref
                return {"status": True, "data": res_json['data']}
            else:
                logging.error(f"Flutterwave Error: {res_json.get('message')}")
                return {"status": False, "message": res_json.get('message')}
        except Exception as e:
            logging.error(f"Request Exception: {e}")
            return {"status": False, "message": str(e)}

    @staticmethod
    def verify_transaction(transaction_id):
        """Verify a transaction with Flutterwave using the transaction ID."""
        # Note: Flutterwave verification usually uses the transaction ID returned in the redirect URL
        # or you can search by tx_ref. For simplicity in Telegram, we'll ask for the ID or check latest.
        url = f"{PaymentManager.BASE_URL}/transactions/{transaction_id}/verify"
        try:
            response = requests.get(url, headers=PaymentManager.HEADERS)
            return response.json()
        except Exception as e:
            logging.error(f"Verification Exception: {e}")
            return {"status": "error", "message": str(e)}

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
